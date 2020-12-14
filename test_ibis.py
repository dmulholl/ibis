#!/usr/bin/env python3
# ------------------------------------------------------------------------------
# Unit tests for the Ibis package.
# ------------------------------------------------------------------------------

import unittest
import datetime

import ibis
from ibis import Template


# ------------------------------------------------------------------------------
# Templates.
# ------------------------------------------------------------------------------


# Loadable templates for testing the 'include' and 'extends' tags.
ibis.loader = ibis.loaders.DictLoader({
    'simple': '{{ var }}',
    'base': (
        '|#|'
        '{% block content %}'
        'base-{{ var }}'
        '{% endblock %}'
        '|#|'
    ),
    'child': (
        '{% extends "base" %}'
        '{% block content %}'
        '{{ super() }}|child-{{ var }}'
        '{% endblock %}'
        ),
    'loop': (
        '{% for i in [1, 2, 3] %}'
        '{% block content %}'
        '{{ i }}'
        '{% endblock %}'
        '{% endfor %}'
    ),
})


# ------------------------------------------------------------------------------
# Tests.
# ------------------------------------------------------------------------------


class BasicInputTests(unittest.TestCase):

    def test_empty_template_string(self):
        template = ''
        rendered = Template(template).render()
        self.assertEqual(rendered, '')

    def test_template_with_no_tags(self):
        template = 'no tags'
        rendered = Template(template).render()
        self.assertEqual(rendered, 'no tags')

    def test_template_with_comments(self):
        template = 'foo{# this is \n a comment #}bar'
        rendered = Template(template).render()
        self.assertEqual(rendered, 'foobar')


class PrintStatementTests(unittest.TestCase):

    def test_print_statement(self):
        template = '{{var}}'
        rendered = Template(template).render(var='foo')
        self.assertEqual(rendered, 'foo')

    def test_escaped_print_statement(self):
        template = '{{{var}}}'
        rendered = Template(template).render(var='<div>')
        self.assertEqual(rendered, '&lt;div&gt;')

    def test_callable(self):
        template = '{{func()}}'
        rendered = Template(template).render(func=lambda: 'foo')
        self.assertEqual(rendered, 'foo')

    def test_callable_with_arg(self):
        template = '{{func("foo")}}'
        rendered = Template(template).render(func=lambda arg: arg)
        self.assertEqual(rendered, 'foo')

    def test_multiple_vars_with_or(self):
        template = '{{var1 or var2}}'
        rendered = Template(template).render(var1=None, var2='foo')
        self.assertEqual(rendered, 'foo')

    def test_multiple_vars_with_pipes(self):
        template = '{{var1 || var2}}'
        rendered = Template(template).render(var1=None, var2='foo')
        self.assertEqual(rendered, 'foo')

    def test_ternary_operator_true(self):
        template = '{{test ?? var1 :: var2}}'
        rendered = Template(template).render(test=True, var1='foo', var2='bar')
        self.assertEqual(rendered, 'foo')

    def test_ternary_operator_false(self):
        template = '{{test ?? var1 :: var2}}'
        rendered = Template(template).render(test=False, var1='foo', var2='bar')
        self.assertEqual(rendered, 'bar')


class FilterMechanismTests(unittest.TestCase):

    def test_filter_with_no_args(self):
        template = '{{var|escape}}'
        rendered = Template(template).render(var='<div>')
        self.assertEqual(rendered, '&lt;div&gt;')

    def test_filter_with_int_arg(self):
        template = '{{var|default(5)}}'
        rendered = Template(template).render(var=None)
        self.assertEqual(rendered, '5')

    def test_filter_with_string_arg(self):
        template = '{{var|default("foo")}}'
        rendered = Template(template).render(var=None)
        self.assertEqual(rendered, 'foo')

    def test_filter_with_multiple_args(self):
        template = '{{var|argtest("bar", 42)}}'
        rendered = Template(template).render(var='foo')
        self.assertEqual(rendered, 'foo|bar|42')

    def test_aliased_filter_name(self):
        template = '{{var|esc}}'
        rendered = Template(template).render(var='<div>')
        self.assertEqual(rendered, '&lt;div&gt;')

    def test_chained_filters(self):
        template = '{{var|default("foo")|upper}}'
        rendered = Template(template).render(var=None)
        self.assertEqual(rendered, 'FOO')

    def test_filtered_literal(self):
        template = '{{"<div>"|escape}}'
        rendered = Template(template).render()
        self.assertEqual(rendered, '&lt;div&gt;')


class FilterFunctionTests(unittest.TestCase):

    def test_default(self):
        template = '{{var|default(101)}}'
        rendered = Template(template).render(var=None)
        self.assertEqual(rendered, '101')

    def test_dtformat(self):
        template = '{{var|dtformat("%Y")}}'
        rendered = Template(template).render(var=datetime.datetime(2000, 1, 1))
        self.assertEqual(rendered, '2000')

    def test_endswith(self):
        template = '{{var|endswith("bar")}}'
        rendered = Template(template).render(var='foobar')
        self.assertEqual(rendered, 'True')

    def test_escape(self):
        template = '{{var|escape}}'
        rendered = Template(template).render(var='''<p>"foo" & 'bar'</p>''')
        self.assertEqual(
            rendered,
            '&lt;p&gt;&quot;foo&quot; &amp; &#x27;bar&#x27;&lt;/p&gt;'
        )

    def test_first(self):
        template = '{{var|first}}'
        rendered = Template(template).render(var=('foo', 'bar'))
        self.assertEqual(rendered, 'foo')

    def test_firsth(self):
        template = '{{var|firsth}}'
        rendered = Template(template).render(var=('foo <h1>bar</h1> baz'))
        self.assertEqual(rendered, 'bar')

    def test_firsth_with_newline(self):
        template = '{{var|firsth}}'
        rendered = Template(template).render(var=('foo <h1>bar\nbar</h1> baz'))
        self.assertEqual(rendered, 'bar\nbar')

    def test_firstp(self):
        template = '{{var|firstp}}'
        rendered = Template(template).render(var=('foo <p>bar</p> baz'))
        self.assertEqual(rendered, 'bar')

    def test_firstp_with_newline(self):
        template = '{{var|firstp}}'
        rendered = Template(template).render(var=('foo <p>bar\nbar</p> baz'))
        self.assertEqual(rendered, 'bar\nbar')

    def test_index(self):
        template = '{{var|index(1)}}'
        rendered = Template(template).render(var=('foo', 'bar'))
        self.assertEqual(rendered, 'bar')

    def test_join(self):
        template = '{{var|join(", ")}}'
        rendered = Template(template).render(var=('foo', 'bar'))
        self.assertEqual(rendered, 'foo, bar')

    def test_last(self):
        template = '{{var|last}}'
        rendered = Template(template).render(var=('foo', 'bar'))
        self.assertEqual(rendered, 'bar')

    def test_len(self):
        template = '{{var|len}}'
        rendered = Template(template).render(var=('foo', 'bar'))
        self.assertEqual(rendered, '2')

    def test_lower(self):
        template = '{{var|lower}}'
        rendered = Template(template).render(var='Foo')
        self.assertEqual(rendered, 'foo')

    def test_repr(self):
        template = '{{var|repr}}'
        rendered = Template(template).render(var=123)
        self.assertEqual(rendered, '123')

    def test_str(self):
        template = '{{var|str}}'
        rendered = Template(template).render(var=123)
        self.assertEqual(rendered, '123')

    def test_striptags(self):
        template = '{{var|striptags}}'
        rendered = Template(template).render(var='foo <em>bar</em> baz')
        self.assertEqual(rendered, 'foo bar baz')

    def test_startswith(self):
        template = '{{var|startswith("foo")}}'
        rendered = Template(template).render(var='foobar')
        self.assertEqual(rendered, 'True')

    def test_truncatechars(self):
        template = '{{"supercalifragilisticexpialidocious"|truncatechars(12)}}'
        rendered = Template(template).render()
        self.assertEqual(rendered, 'supercali...')

    def test_truncatewords(self):
        template = '{{"lorem ipsum dolor sit amet"|truncatewords(3)}}'
        rendered = Template(template).render(var='supercalifragilistic')
        self.assertEqual(rendered, 'lorem ipsum dolor [...]')

    def test_upper(self):
        template = '{{var|upper}}'
        rendered = Template(template).render(var='Foo')
        self.assertEqual(rendered, 'FOO')

    def test_wrap(self):
        template = '{{var|wrap("p")}}'
        rendered = Template(template).render(var='foo')
        self.assertEqual(rendered, '<p>foo</p>')

    def test_if_undefined_case1(self):
        template = '{{var|if_undefined("foo")}}'
        rendered = Template(template).render()
        self.assertEqual(rendered, 'foo')

    def test_if_undefined_case2(self):
        template = '{{var|if_undefined("foo")}}'
        rendered = Template(template).render(var=123)
        self.assertEqual(rendered, '123')

    def test_is_defined_case1(self):
        template = '{% if var|is_defined %}foo{% else %}bar{% endif %}'
        rendered = Template(template).render()
        self.assertEqual(rendered, 'bar')

    def test_is_defined_case2(self):
        template = '{% if var|is_defined %}foo{% else %}bar{% endif %}'
        rendered = Template(template).render(var=123)
        self.assertEqual(rendered, 'foo')


class BuiltinFunctionTests(unittest.TestCase):

    def test_range(self):
        template = '{% for i in range(4) %}{{i}}.{% endfor %}'
        rendered = Template(template).render()
        self.assertEqual(rendered, '0.1.2.3.')

    def test_is_defined_func_case1(self):
        template = '{% if is_defined("var") %}foo{% else %}bar{% endif %}'
        rendered = Template(template).render()
        self.assertEqual(rendered, 'bar')

    def test_is_defined_func_case2(self):
        template = '{% if is_defined("var") %}foo{% else %}bar{% endif %}'
        rendered = Template(template).render(var=123)
        self.assertEqual(rendered, 'foo')


class IfTagTests(unittest.TestCase):

    def test_if_true(self):
        template = '{% if num > 5 %}foo{% endif %}'
        rendered = Template(template).render(num=7)
        self.assertEqual(rendered, 'foo')

    def test_if_false(self):
        template = '{% if num > 5 %}foo{% endif %}'
        rendered = Template(template).render(num=3)
        self.assertEqual(rendered, '')

    def test_if_else_true(self):
        template = '{% if num > 5 %}foo{% else %}bar{% endif %}'
        rendered = Template(template).render(num=7)
        self.assertEqual(rendered, 'foo')

    def test_if_else_false(self):
        template = '{% if num > 5 %}foo{% else %}bar{% endif %}'
        rendered = Template(template).render(num=3)
        self.assertEqual(rendered, 'bar')

    def test_truthiness(self):
        template = '{% if num %}foo{% endif %}'
        rendered = Template(template).render(num=7)
        self.assertEqual(rendered, 'foo')

    def test_falsiness(self):
        template = '{% if num %}foo{% endif %}'
        rendered = Template(template).render(num=0)
        self.assertEqual(rendered, '')

    def test_if_not_truthy(self):
        template = '{% if not num %}foo{% endif %}'
        rendered = Template(template).render(num=7)
        self.assertEqual(rendered, '')

    def test_if_not_falsy(self):
        template = '{% if not num %}foo{% endif %}'
        rendered = Template(template).render(num=0)
        self.assertEqual(rendered, 'foo')

    def test_if_in_with_context_lookup(self):
        template = '{% if "Mon" in days %}foo{% endif %}'
        rendered = Template(template).render(days=['Mon', 'Tue', 'Wed'])
        self.assertEqual(rendered, 'foo')
        template = '{% if "Fri" in days %}foo{% endif %}'
        rendered = Template(template).render(days=['Mon', 'Tue', 'Wed'])
        self.assertEqual(rendered, '')

    def test_if_in_with_literal(self):
        template = '{% if var in [1, 2, 3] %}foo{% endif %}'
        rendered = Template(template).render(var=1)
        self.assertEqual(rendered, 'foo')
        template = '{% if var in "abc" %}foo{% endif %}'
        rendered = Template(template).render(var='a')
        self.assertEqual(rendered, 'foo')

    def test_if_not_in(self):
        template = '{% if "Mon" not in days %}foo{% endif %}'
        rendered = Template(template).render(days=['Mon', 'Tue', 'Wed'])
        self.assertEqual(rendered, '')
        template = '{% if "Fri" not in days %}foo{% endif %}'
        rendered = Template(template).render(days=['Mon', 'Tue', 'Wed'])
        self.assertEqual(rendered, 'foo')

    def test_if_with_nested_for(self):
        template =  '{% if num > 5 %}'
        template += '{% for day in days %}{{day}}{% endfor %}'
        template += '{% endif %}'
        rendered = Template(template).render(num=7, days=['Mon', 'Tue', 'Wed'])
        self.assertEqual(rendered, 'MonTueWed')

    def test_if_elif(self):
        template = '{% if num > 5 %}foo{% elif num > 3 %}bar{% endif %}'
        rendered = Template(template).render(num=7)
        self.assertEqual(rendered, 'foo')
        rendered = Template(template).render(num=4)
        self.assertEqual(rendered, 'bar')

    def test_if_elif_elif(self):
        template =  '{% if num > 5 %}foo'
        template += '{% elif num > 3 %}bar'
        template += '{% elif num > 1 %}baz'
        template += '{% endif %}'
        rendered = Template(template).render(num=6)
        self.assertEqual(rendered, 'foo')
        rendered = Template(template).render(num=4)
        self.assertEqual(rendered, 'bar')
        rendered = Template(template).render(num=2)
        self.assertEqual(rendered, 'baz')

    def test_if_elif_else(self):
        template =  '{% if num > 5 %}foo'
        template += '{% elif num > 3 %}bar'
        template += '{% else %}baz'
        template += '{% endif %}'
        rendered = Template(template).render(num=6)
        self.assertEqual(rendered, 'foo')
        rendered = Template(template).render(num=4)
        self.assertEqual(rendered, 'bar')
        rendered = Template(template).render(num=2)
        self.assertEqual(rendered, 'baz')


class IfCombinationTests(unittest.TestCase):

    def test_if_and(self):
        template = '{% if arg1 and arg2 %}foo{% endif %}'
        rendered = Template(template).render(arg1=True, arg2=True)
        self.assertEqual(rendered, 'foo')
        rendered = Template(template).render(arg1=False, arg2=True)
        self.assertEqual(rendered, '')
        rendered = Template(template).render(arg1=True, arg2=False)
        self.assertEqual(rendered, '')
        rendered = Template(template).render(arg1=False, arg2=False)
        self.assertEqual(rendered, '')

    def test_if_or(self):
        template = '{% if arg1 or arg2 %}foo{% endif %}'
        rendered = Template(template).render(arg1=True, arg2=True)
        self.assertEqual(rendered, 'foo')
        rendered = Template(template).render(arg1=False, arg2=True)
        self.assertEqual(rendered, 'foo')
        rendered = Template(template).render(arg1=True, arg2=False)
        self.assertEqual(rendered, 'foo')
        rendered = Template(template).render(arg1=False, arg2=False)
        self.assertEqual(rendered, '')

    def test_if_precedence(self):
        template = '{% if arg1 and arg2 or arg3 %}foo{% endif %}'
        rendered = Template(template).render(arg1=True, arg2=True, arg3=True)
        self.assertEqual(rendered, 'foo')
        rendered = Template(template).render(arg1=True, arg2=True, arg3=False)
        self.assertEqual(rendered, 'foo')
        rendered = Template(template).render(arg1=False, arg2=False, arg3=True)
        self.assertEqual(rendered, 'foo')


class ForTagTests(unittest.TestCase):

    def test_forloop_with_context_lookup(self):
        template = '{% for day in days %}{{day}}{% endfor %}'
        rendered = Template(template).render(days=['Mon', 'Tue', 'Wed'])
        self.assertEqual(rendered, 'MonTueWed')

    def test_forloop_with_literal(self):
        template = '{% for i in [1, 2, 3] %}{{i}}{% endfor %}'
        rendered = Template(template).render()
        self.assertEqual(rendered, '123')

    def test_forloop_with_nested_if(self):
        template =  '{% for i in [1, 2, 3] %}'
        template += '{% if i > 1 %}{{i}}{% endif %}'
        template += '{% endfor %}'
        rendered = Template(template).render()
        self.assertEqual(rendered, '23')

    def test_forloop_with_nested_forloop(self):
        template =  '{% for i in [1, 2] %}'
        template += '{% for j in "ab" %}{{i}}{{j}}.{% endfor %}'
        template += '{% endfor %}'
        rendered = Template(template).render()
        self.assertEqual(rendered, '1a.1b.2a.2b.')

    def test_forloop_with_empty_block(self):
        template = '{% for i in var %}{{i}}{% empty %}empty{% endfor %}'
        rendered = Template(template).render(var=[])
        self.assertEqual(rendered, 'empty')

    def test_forloop_meta(self):
        template = '{% for i in var %}{{loop.index}}{% endfor %}'
        rendered = Template(template).render(var='abcd')
        self.assertEqual(rendered, '0123')
        template =  '{% for i in var %}'
        template += '{% if loop.is_first %}{{i}}{% endif %}'
        template += '{% endfor %}'
        rendered = Template(template).render(var='abcd')
        self.assertEqual(rendered, 'a')

    def test_forloop_with_multiple_loop_vars(self):
        template = '{% for x, y in points %}({{x}},{{y}}){% endfor %}'
        rendered = Template(template).render(points=[(1, 2), (3, 4), (5, 6)])
        self.assertEqual(rendered, '(1,2)(3,4)(5,6)')


class CycleTagTests(unittest.TestCase):

    def test_cycle_block(self):
        template =  '{% for i in [1, 2, 3, 4] %}'
        template += '.{% cycle "odd", "even" %}'
        template += '{% endfor %}'
        rendered = Template(template).render(var='foo')
        self.assertEqual(rendered, '.odd.even.odd.even')

    def test_cycle_block_empty(self):
        template = '{% for i in [1, 2, 3, 4] %}.{% cycle [] %}{% endfor %}'
        rendered = Template(template).render(var='foo')
        self.assertEqual(rendered, '....')


class WithTagTests(unittest.TestCase):

    def test_with_block_with_literal(self):
        template = '{% with var = "foo" %}{{var}}{% endwith %}'
        rendered = Template(template).render()
        self.assertEqual(rendered, 'foo')

    def test_with_block_with_variable(self):
        template = '{% with var = foo.bar("baz") %}{{var}}{% endwith %}'
        rendered = Template(template).render(foo={'bar': lambda x: x})
        self.assertEqual(rendered, 'baz')


class SpacelessTagTests(unittest.TestCase):

    def test_spaceless_block(self):
        template =  '{% spaceless %}'
        template += '\n<ul>\n<li> foo </li>  </ul> '
        template += '{% endspaceless %}'
        rendered = Template(template).render()
        self.assertEqual(rendered, '<ul><li> foo </li></ul>')


class TrimTagTests(unittest.TestCase):

    def test_trim_block(self):
        template =  '{% trim %}'
        template += '\n  foo bar baz\t  '
        template += '{% endtrim %}'
        rendered = Template(template).render()
        self.assertEqual(rendered, 'foo bar baz')


class IncludeTagTests(unittest.TestCase):

    def test_working_include(self):
        template_string = '{% include "simple" %}'
        rendered = Template(template_string).render(var='foo')
        self.assertEqual(rendered, 'foo')

    def test_malformed_include_missing_name(self):
        template_string = '{% include %}'
        with self.assertRaises(ibis.errors.TemplateSyntaxError):
            Template(template_string).render()

    def test_malformed_include_invalid_literal(self):
        template_string = '{% include 123 %}'
        with self.assertRaises(ibis.errors.TemplateSyntaxError):
            Template(template_string).render()

    def test_include_invalid_variable(self):
        template_string = '{% include var %}'
        with self.assertRaises(ibis.errors.TemplateRenderingError):
            Template(template_string).render(var=None)

    def test_include_undefined_variable(self):
        template_string = '{% include var %}'
        with self.assertRaises(ibis.errors.TemplateRenderingError):
            Template(template_string).render()


class TemplateInheritanceTests(unittest.TestCase):

    def test_single_level_inheritance(self):
        template =  '{% extends "base" %}'
        template += '{% block content %}'
        template += 'override-{{ var }}'
        template += '{% endblock %}'
        rendered = Template(template).render(var='foo')
        self.assertEqual(rendered, '|#|override-foo|#|')

    def test_single_level_inheritance_with_super(self):
        template =  '{% extends "base" %}'
        template += '{% block content %}'
        template += '{{ super() }}|override-{{ var }}'
        template += '{% endblock %}'
        rendered = Template(template).render(var='foo')
        self.assertEqual(rendered, '|#|base-foo|override-foo|#|')

    def test_double_level_inheritance(self):
        template =  '{% extends "child" %}'
        template += '{% block content %}'
        template += 'override-{{ var }}'
        template += '{% endblock %}'
        rendered = Template(template).render(var='foo')
        self.assertEqual(rendered, '|#|override-foo|#|')

    def test_double_level_inheritance_with_super(self):
        template =  '{% extends "child" %}'
        template += '{% block content %}'
        template += '{{ super() }}|override-{{var}}'
        template += '{% endblock %}'
        rendered = Template(template).render(var='foo')
        self.assertEqual(rendered, '|#|base-foo|child-foo|override-foo|#|')

    def test_parent_block_in_loop(self):
        template =  '{% extends "loop" %}'
        template += '{% block content %}'
        template += '{{ i }}#'
        template += '{% endblock %}'
        rendered = Template(template).render()
        self.assertEqual(rendered, '1#2#3#')

    def test_parent_block_in_loop_with_super(self):
        template =  '{% extends "loop" %}'
        template += '{% block content %}'
        template += '{{ super() }}#'
        template += '{% endblock %}'
        rendered = Template(template).render()
        self.assertEqual(rendered, '1#2#3#')


class StrictModeTests(unittest.TestCase):

    def test_defined_variable(self):
        template = '{{ var }}'
        rendered = Template(template).render(var=123, strict_mode=True)
        self.assertEqual(rendered, '123')

    def test_undefined_variable(self):
        template = '{{ var }}'
        with self.assertRaises(ibis.errors.UndefinedVariable):
            rendered = Template(template).render(strict_mode=True)

    def test_is_defined_func_case1(self):
        template = '{% if is_defined("var") %}foo{% else %}bar{% endif %}'
        rendered = Template(template).render(strict_mode=True)
        self.assertEqual(rendered, 'bar')

    def test_is_defined_func_case2(self):
        template = '{% if is_defined("var") %}foo{% else %}bar{% endif %}'
        rendered = Template(template).render(var=123, strict_mode=True)
        self.assertEqual(rendered, 'foo')


class EmptyTagTests(unittest.TestCase):

    def test_empty_tag(self):
        template_string = '{%%}'
        with self.assertRaises(ibis.errors.TemplateSyntaxError):
            template = Template(template_string)

    def test_whitespace_tag(self):
        template_string = '{%    %}'
        with self.assertRaises(ibis.errors.TemplateSyntaxError):
            template = Template(template_string)


class ErrorThrower:
    @property
    def raises_error(self):
        raise Exception("Nobody expects an unexpected error!")


@ibis.nodes.register('evil_parser')
class EvilParser(ibis.nodes.Node):
    def process_token(self, token):
        raise Exception("Nobody expects an evil parser!")


@ibis.nodes.register('evil_renderer')
class EvilRenderer(ibis.nodes.Node):
    def wrender(self, context):
        raise Exception("Nobody expects an evil renderer!")


class UnexpectedErrorTests(unittest.TestCase):

    def test_unexpected_property_error(self):
        template_string = '{{ obj.raises_error }}'
        with self.assertRaises(ibis.errors.TemplateRenderingError):
            rendered = Template(template_string).render(obj=ErrorThrower())

    def test_unexpected_parsing_error(self):
        template_string = '{% evil_parser %}'
        with self.assertRaises(ibis.errors.TemplateSyntaxError):
            template = Template(template_string)

    def test_unexpected_rendering_error(self):
        template_string = '{% evil_renderer %}'
        with self.assertRaises(ibis.errors.TemplateRenderingError):
            rendered = Template(template_string).render()


class TestObject:

    def __init__(self):
        self.int_attr = 999
        self.str_attr = "foo"

    @property
    def prop(self):
        return "foobar"


test_dict = {
    "abc": "foo",
    "123": "bar",
}


test_list = ["foo", "bar"]


class VariableLookupTests(unittest.TestCase):

    def test_undefined_variable_case1(self):
        template_string = '{{ var }}'
        rendered = Template(template_string).render()
        self.assertEqual(rendered, '')

    def test_undefined_variable_case2(self):
        template_string = '{{ var.foo }}'
        rendered = Template(template_string).render()
        self.assertEqual(rendered, '')

    def test_undefined_variable_case3(self):
        template_string = '{{ var.foo }}'
        rendered = Template(template_string).render(var=123)
        self.assertEqual(rendered, '')

    def test_undefined_variable_case1_strict(self):
        template_string = '{{ var }}'
        with self.assertRaises(ibis.errors.UndefinedVariable):
            rendered = Template(template_string).render(strict_mode=True)

    def test_undefined_variable_case2_strict(self):
        template_string = '{{ var.foo }}'
        with self.assertRaises(ibis.errors.UndefinedVariable):
            rendered = Template(template_string).render(strict_mode=True)

    def test_undefined_variable_case3_strict(self):
        template_string = '{{ var.foo }}'
        with self.assertRaises(ibis.errors.UndefinedVariable):
            rendered = Template(template_string).render(var=123, strict_mode=True)

    def test_object_with_int_attribute(self):
        template_string = '{{ obj.int_attr }}'
        rendered = Template(template_string).render(obj=TestObject())
        self.assertEqual(rendered, '999')

    def test_object_with_str_attribute(self):
        template_string = '{{ obj.str_attr }}'
        rendered = Template(template_string).render(obj=TestObject())
        self.assertEqual(rendered, 'foo')

    def test_object_with_property(self):
        template_string = '{{ obj.prop }}'
        rendered = Template(template_string).render(obj=TestObject())
        self.assertEqual(rendered, 'foobar')

    def test_dict_with_alphabetic_key(self):
        template_string = '{{ somedict.abc }}'
        rendered = Template(template_string).render(somedict=test_dict)
        self.assertEqual(rendered, 'foo')

    def test_dict_with_numeric_key(self):
        template_string = '{{ somedict.123 }}'
        rendered = Template(template_string).render(somedict=test_dict)
        self.assertEqual(rendered, 'bar')

    def test_list_with_numeric_index_0(self):
        template_string = '{{ somelist.0 }}'
        rendered = Template(template_string).render(somelist=test_list)
        self.assertEqual(rendered, 'foo')

    def test_list_with_numeric_index_1(self):
        template_string = '{{ somelist.1 }}'
        rendered = Template(template_string).render(somelist=test_list)
        self.assertEqual(rendered, 'bar')

    def test_list_with_numeric_index_out_of_range(self):
        template_string = '{{ somelist.99 }}'
        rendered = Template(template_string).render(somelist=test_list)
        self.assertEqual(rendered, '')

    def test_list_with_numeric_index_out_of_range_strict(self):
        template_string = '{{ somelist.99 }}'
        with self.assertRaises(ibis.errors.UndefinedVariable):
            rendered = Template(template_string).render(somelist=test_list, strict_mode=True)

    def test_stacked_numeric_indices(self):
        template_string = '{{ somelist.0.0 }}--{{ somelist.0.1 }}--{{ somelist.0.2 }}'
        rendered = Template(template_string).render(somelist=test_list)
        self.assertEqual(rendered, 'f--o--o')


class ContextShadowingTests(unittest.TestCase):

    def test_variable_name_template(self):
        template_string = '{{ template }}'
        rendered = Template(template_string).render(template="foo")
        self.assertEqual(rendered, 'foo')

    def test_variable_name_data(self):
        template_string = '{{ data }}'
        rendered = Template(template_string).render(data="foo")
        self.assertEqual(rendered, 'foo')

    def test_variable_name_resolve(self):
        template_string = '{{ resolve }}'
        rendered = Template(template_string).render(resolve="foo")
        self.assertEqual(rendered, 'foo')


class ParsingErrorTests(unittest.TestCase):

    def test_unrecognised_tag(self):
        template_string = '{% foobar %}'
        with self.assertRaises(ibis.errors.TemplateSyntaxError):
            template = Template(template_string)

    def test_unexpected_closing_tag(self):
        template_string = '{% endif %}'
        with self.assertRaises(ibis.errors.TemplateSyntaxError):
            template = Template(template_string)

    def test_wrong_closing_tag(self):
        template_string = '{% if var %}{% endfor %}'
        with self.assertRaises(ibis.errors.TemplateSyntaxError):
            template = Template(template_string)

    def test_missing_closing_tag(self):
        template_string = '{% if var %}'
        with self.assertRaises(ibis.errors.TemplateSyntaxError):
            template = Template(template_string)


class LexingErrorTests(unittest.TestCase):

    def test_unclosed_comment_tag(self):
        template_string = '{# foobar '
        with self.assertRaises(ibis.errors.TemplateLexingError):
            template = Template(template_string)

    def test_unclosed_eprint_tag(self):
        template_string = '{{{ foobar '
        with self.assertRaises(ibis.errors.TemplateLexingError):
            template = Template(template_string)

    def test_unclosed_print_tag(self):
        template_string = '{{ foobar '
        with self.assertRaises(ibis.errors.TemplateLexingError):
            template = Template(template_string)

    def test_unclosed_instruction_tag(self):
        template_string = '{% foobar '
        with self.assertRaises(ibis.errors.TemplateLexingError):
            template = Template(template_string)


if __name__ == '__main__':
    unittest.main()

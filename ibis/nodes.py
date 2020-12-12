import ast
import operator
import re
import itertools
import collections
import ibis

from . import utils
from . import filters
from . import errors


# Dictionary of registered keywords for instruction tags.
instruction_keywords = {}


# List of registered endwords for instruction tags with block scope.
instruction_endwords = []


# Decorator function for registering handler classes for instruction tags.
# Registering an endword gives the instruction tag block scope.
def register(keyword, endword=None):

    def register_node_class(node_class):
        instruction_keywords[keyword] = (node_class, endword)
        if endword:
            instruction_endwords.append(endword)
        return node_class

    return register_node_class


# Helper class for evaluating expression strings.
#
# An Expression object is initialized with an expression string parsed from a template. An
# expression string can contain a variable name or a Python literal, optionally followed by a
# sequence of filters.
#
# The Expression object handles the rather convoluted process of parsing the string, evaluating
# the literal or resolving the variable, calling the variable if it resolves to a callable, and
# applying the filters to the resulting object. The consumer simply needs to call the expression's
# .eval() method and supply an appropriate Context object.
#
# Examples of valid expression syntax include:
#
#     foo.bar.baz|default('bam')|escape
#     'foo', 'bar', 'baz'|random
#
# Arguments can be passed to callables using bracket syntax:
#
#     foo.bar.baz('bam')|filter(25, 'text')
#
class Expression:

    re_func_call = re.compile(r'^([a-zA-Z_][a-zA-Z0-9_.]*)[(](.*)[)]$')

    def __init__(self, expr, token):
        self.token = token
        self.filters = []
        pipe_split = utils.splitc(expr.strip(), '|', strip=True)
        self._parse_primary_expr(pipe_split[0])
        self._parse_filters(pipe_split[1:])
        if self.is_literal:
            self.literal = self._apply_filters_to_literal(self.literal)

    def _parse_primary_expr(self, expr):
        try:
            self.literal = ast.literal_eval(expr)
            self.is_literal = True
        except:
            self.is_func_call, self.varstring, self.func_args = self._try_parse_as_func_call(expr)
            self.is_literal = False

    def _try_parse_as_func_call(self, expr):
        match = self.re_func_call.match(expr)
        if not match:
            return False, expr, []
        func_name = match.group(1)
        func_args = utils.splitc(match.group(2), ',', True, True)
        for index, arg in enumerate(func_args):
            try:
                func_args[index] = ast.literal_eval(arg)
            except Exception as err:
                msg = f"Unparsable argument '{arg}' in template '{self.token.template_id}', "
                msg += f"line {self.token.line_number}. "
                msg += f"Arguments must be valid Python literals."
                raise errors.TemplateSyntaxError(msg, self.token) from err
        return True, func_name, func_args

    def _parse_filters(self, filter_list):
        for filter_expr in filter_list:
            _, filter_name, filter_args = self._try_parse_as_func_call(filter_expr)
            if filter_name in filters.filtermap:
                self.filters.append((filter_name, filters.filtermap[filter_name], filter_args))
            else:
                msg = f"Unrecognised filter name '{filter_name}' in template '{self.token.template_id}', "
                msg += f"line {self.token.line_number}."
                raise errors.TemplateSyntaxError(msg, self.token)

    def _apply_filters_to_literal(self, obj):
        for name, func, args in self.filters:
            try:
                obj = func(obj, *args)
            except Exception as err:
                msg = f"Error applying filter '{name}' to literal "
                msg += f"in template '{self.token.template_id}', line {self.token.line_number}."
                raise errors.TemplateSyntaxError(msg, self.token) from err
        return obj

    def eval(self, context):
        if self.is_literal:
            return self.literal
        else:
            return self._resolve_variable(context)

    def _resolve_variable(self, context):
        obj = context.resolve(self.varstring, self.token)
        if self.is_func_call:
            try:
                obj = obj(*self.func_args)
            except Exception as err:
                msg = f"Error calling function '{self.varstring}' "
                msg += f"in template '{self.token.template_id}', line {self.token.line_number}."
                raise errors.TemplateRenderingError(msg, self.token) from err
        return self._apply_filters_to_variable(obj)

    def _apply_filters_to_variable(self, obj):
        for name, func, args in self.filters:
            try:
                obj = func(obj, *args)
            except Exception as err:
                msg = f"Error applying filter '{name}' to variable "
                msg += f"in template '{self.token.template_id}', line {self.token.line_number}."
                raise errors.TemplateRenderingError(msg, self.token) from err
        return obj


# Base class for all node objects. To render a node into a string call its .render() method.
# Subclasses shouldn't override the base .render() method; instead they should override
# .wrender() which ensures that any uncaught exceptions are wrapped in a TemplateRenderingError.
class Node:

    def __init__(self, token=None, children=None):
        self.token = token
        self.children = children or []
        try:
            self.process_token(token)
        except errors.TemplateError:
            raise
        except Exception as err:
            if token:
                tagname = f"'{token.keyword}'" if token.type == "INSTRUCTION" else token.type
                msg = f"An unexpected error occurred while parsing the {tagname} tag "
                msg += f"in template '{token.template_id}', line {token.line_number}: "
                msg += f"{err.__class__.__name__}: {err}"
            else:
                msg = f"Unexpected syntax error: {err.__class__.__name__}: {err}"
            raise errors.TemplateSyntaxError(msg, token) from err

    def __str__(self):
        return self.to_str()

    def to_str(self, depth=0):
        output = ["·  " * depth + f"{self.__class__.__name__}"]
        for child in self.children:
            output.append(child.to_str(depth + 1))
        return "\n".join(output)

    def render(self, context):
        try:
            return self.wrender(context)
        except errors.TemplateError:
            raise
        except Exception as err:
            if self.token:
                tagname = f"'{self.token.keyword}'" if self.token.type == "INSTRUCTION" else self.token.type
                msg = f"An unexpected error occurred while rendering the {tagname} tag "
                msg += f"in template '{self.token.template_id}', line {self.token.line_number}: "
                msg += f"{err.__class__.__name__}: {err}"
            else:
                msg = f"Unexpected rendering error: {err.__class__.__name__}: {err}"
            raise errors.TemplateRenderingError(msg, self.token) from err

    def wrender(self, context):
        return ''.join(child.render(context) for child in self.children)

    def process_token(self, token):
        pass

    def exit_scope(self):
        pass

    def split_children(self, delimiter_class):
        for index, child in enumerate(self.children):
            if isinstance(child, delimiter_class):
                return self.children[:index], child, self.children[index+1:]
        return self.children, None, []


# TextNodes represent ordinary template text, i.e. text not enclosed in tag delimiters.
class TextNode(Node):

    def wrender(self, context):
        return self.token.text


# A PrintNode evaluates an expression and prints its result. Multiple expressions can be listed
# separated by 'or' or '||'. The first expression to resolve to a truthy value will be printed.
# (If none of the expressions are truthy the final value will be printed regardless.)
#
#     {{ <expr> or <expr> or <expr> }}
#
# Alternatively, print statements can use the ternary operator: ?? ::
#
#     {{ <test-expr> ?? <expr1> :: <expr2> }}
#
# If <test-expr> is truthy, <expr1> will be printed, otherwise <expr2> will be printed.
#
# Note that *either* 'or'-chaining or the ternary operator can be used in a single print statement,
# but not both.
class PrintNode(Node):

    escape_content = False

    def process_token(self, token):

        # Check for a ternary operator.
        chunks = utils.splitre(token.text, (r'\?\?', r'\:\:'), True)
        if len(chunks) == 5 and chunks[1] == '??' and chunks[3] == '::':
            self.is_ternary = True
            self.test_expr = Expression(chunks[0], token)
            self.true_branch_expr = Expression(chunks[2], token)
            self.false_branch_expr = Expression(chunks[4], token)

        # Look for a list of 'or' separated expressions.
        else:
            self.is_ternary = False
            exprs = utils.splitre(token.text, (r'\s+or\s+', r'\|\|'))
            self.exprs = [Expression(e, token) for e in exprs]

    def wrender(self, context):
        if self.is_ternary:
            if self.test_expr.eval(context):
                content = self.true_branch_expr.eval(context)
            else:
                content = self.false_branch_expr.eval(context)
        else:
            for expr in self.exprs:
                content = expr.eval(context)
                if content:
                    break

        if self.escape_content:
            return filters.escape(str(content))
        else:
            return str(content)


# PrintNode with automatic escaping for content.
class EscapedPrintNode(PrintNode):
    escape_content = True


# ForNodes implement `for ... in ...` looping over iterables.
#
#     {% for <var> in <expr> %} ... [ {% empty %} ... ] {% endfor %}
#
# ForNodes support unpacking into multiple loop variables:
#
#     {% for <var1>, <var2> in <expr> %}
#
@register('for', 'endfor')
class ForNode(Node):

    regex = re.compile(r'for\s+(\w+(?:,\s*\w+)*)\s+in\s+(.+)')

    def process_token(self, token):
        match = self.regex.match(token.text)
        if match is None:
            msg = f"Malformed 'for' tag in template '{token.template_id}', "
            msg += f"line {token.line_number}."
            raise errors.TemplateSyntaxError(msg, token)
        self.loopvars = [var.strip() for var in match.group(1).split(',')]
        self.expr = Expression(match.group(2), token)

    def wrender(self, context):
        collection = self.expr.eval(context)
        if collection and hasattr(collection, '__iter__'):
            collection = list(collection)
            length = len(collection)
            unpack = len(self.loopvars) > 1
            output = []
            for index, item in enumerate(collection):
                context.push()
                if unpack:
                    try:
                        unpacked = dict(zip(self.loopvars, item))
                    except Exception as err:
                        msg = f"Unpacking error in template '{self.token.template_id}', "
                        msg += f"line {self.token.line_number}."
                        raise errors.TemplateRenderingError(msg, self.token) from err
                    else:
                        context.update(unpacked)
                else:
                    context[self.loopvars[0]] = item
                context['loop'] = {
                    'index': index,
                    'count': index + 1,
                    'length': length,
                    'is_first': index == 0,
                    'is_last': index == length - 1,
                    'parent': context.get('loop'),
                }
                output.append(self.for_branch.render(context))
                context.pop()
            return ''.join(output)
        else:
            return self.empty_branch.render(context)

    def exit_scope(self):
        for_nodes, _, empty_nodes = self.split_children(EmptyNode)
        self.for_branch = Node(None, for_nodes)
        self.empty_branch = Node(None, empty_nodes)


# Delimiter node to implement for/empty branching.
@register('empty')
class EmptyNode(Node):
    pass


# IfNodes implement if/elif/else branching.
#
#     {% if [not] <expr> %} ... {% endif %}
#     {% if [not] <expr> <operator> <expr> %} ... {% endif %}
#     {% if <...> %} ... {% elif <...> %} ... {% else %} ... {% endif %}
#
# IfNodes support 'and' and 'or' conjunctions; 'and' has higher precedence so:
#
#     if a and b or c and d
#
# is treated as:
#
#     if (a and b) or (c and d)
#
# Note that explicit brackets are not supported.
@register('if', 'endif')
class IfNode(Node):

    condition = collections.namedtuple('Condition', 'negated lhs op rhs')

    re_condition = re.compile(r'''
        (not\s+)?(.+?)\s+(==|!=|<|>|<=|>=|not[ ]in|in)\s+(.+)
        |
        (not\s+)?(.+)
        ''', re.VERBOSE
    )

    operators = {
        '==': operator.eq,
        '!=': operator.ne,
        '<': operator.lt,
        '>': operator.gt,
        '<=': operator.le,
        '>=': operator.ge,
        'in': lambda a, b: a in b,
        'not in': lambda a, b: a not in b,
    }

    def process_token(self, token):
        self.tag = token.keyword
        try:
            conditions = token.text.split(None, 1)[1]
        except:
            msg = f"Malformed '{self.tag}' tag in template '{token.template_id}', "
            msg += f"line {token.line_number}."
            raise errors.TemplateSyntaxError(msg, token) from None

        self.condition_groups = [
            [
                self.parse_condition(condstr)
                for condstr in utils.splitre(or_block, (r'\s+and\s+', r'&&'))
            ]
            for or_block in utils.splitre(conditions, (r'\s+or\s+', r'\|\|'))
        ]

    def parse_condition(self, condstr):
        match = self.re_condition.match(condstr)
        if match.group(2):
            return self.condition(
                negated = bool(match.group(1)),
                lhs = Expression(match.group(2), self.token),
                op = self.operators[match.group(3)],
                rhs = Expression(match.group(4), self.token),
            )
        else:
            return self.condition(
                negated = bool(match.group(5)),
                lhs = Expression(match.group(6), self.token),
                op = None,
                rhs = None,
            )

    def eval_condition(self, cond, context):
        try:
            if cond.op:
                result = cond.op(cond.lhs.eval(context), cond.rhs.eval(context))
            else:
                result = operator.truth(cond.lhs.eval(context))
        except Exception as err:
            msg = f"An exception was raised while evaluating the condition in the "
            msg += f"'{self.tag}' tag in template '{self.token.template_id}', "
            msg += f"line {self.token.line_number}."
            raise errors.TemplateRenderingError(msg, self.token) from err
        if cond.negated:
            result = not result
        return result

    def wrender(self, context):
        for condition_group in self.condition_groups:
            for condition in condition_group:
                is_true = self.eval_condition(condition, context)
                if not is_true:
                    break
            if is_true:
                break
        if is_true:
            return self.true_branch.render(context)
        else:
            return self.false_branch.render(context)

    def exit_scope(self):
        if_nodes, elif_node, elif_nodes = self.split_children(ElifNode)
        if elif_node:
            self.true_branch = Node(None, if_nodes)
            self.false_branch = IfNode(elif_node.token, elif_nodes)
            self.false_branch.exit_scope()
            return
        if_nodes, _, else_nodes = self.split_children(ElseNode)
        self.true_branch = Node(None, if_nodes)
        self.false_branch = Node(None, else_nodes)


# Delimiter node to implement if/elif branching.
@register('elif')
class ElifNode(Node):
    pass


# Delimiter node to implement if/else branching.
@register('else')
class ElseNode(Node):
    pass


# CycleNodes cycle over an iterable expression.
#
#     {% cycle <expr> %}
#
# Each time the node is evaluated it will render the next value in the sequence, looping once it
# reaches the end; e.g.
#
#     {% cycle 'odd', 'even' %}
#
# will alternate continuously between printing 'odd' and 'even'.
@register('cycle')
class CycleNode(Node):

    def process_token(self, token):
        try:
            tag, arg = token.text.split(None, 1)
        except:
            msg = f"Malformed 'cycle' tag in template '{token.template_id}', "
            msg += f"line {token.line_number}."
            raise errors.TemplateSyntaxError(msg, token) from None
        self.expr = Expression(arg, token)

    def wrender(self, context):
        # We store our state info on the context object to avoid a threading
        # mess if the template is being simultaneously rendered by multiple
        # threads.
        if not self in context.stash:
            items = self.expr.eval(context)
            if not hasattr(items, '__iter__'):
                items = ''
            context.stash[self] = itertools.cycle(items)
        iterator = context.stash[self]
        return str(next(iterator, ''))


# IncludeNodes include a sub-template.
#
#     {% include <expr> %}
#
# Requires a template name which can be supplied as either a string literal or a variable
# resolving to a string. This name will be passed to the registered template loader.
@register('include')
class IncludeNode(Node):

    def process_token(self, token):
        try:
            tag, arg = token.text.split(None, 1)
        except:
            msg = f"Malformed 'include' tag in template '{token.template_id}', "
            msg += f"line {token.line_number}."
            raise errors.TemplateSyntaxError(msg, token) from None
        expr = Expression(arg, token)

        if expr.is_literal:
            if isinstance(expr.literal, str):
                if ibis.loader:
                    template = ibis.loader(expr.literal)
                    self.children.append(template.root_node)
                else:
                    msg = f"No template loader has been specified. "
                    msg += f"A template loader is required by the 'include' tag in "
                    msg += f"template '{token.template_id}', line {token.line_number}."
                    raise errors.TemplateLoadError(msg)
            else:
                msg = f"Malformed 'include' tag in template '{token.template_id}', "
                msg += f"line {token.line_number}. The template name should be a quoted string "
                msg += f"literal or a variable name."
                raise errors.TemplateSyntaxError(msg, token)
        else:
            self.expr = expr
            self.arg = arg

    def wrender(self, context):
        if self.children:
            return ''.join(child.render(context) for child in self.children)
        else:
            template_name = self.expr.eval(context)
            if isinstance(template_name, str):
                if ibis.loader:
                    template = ibis.loader(template_name)
                    return template.root_node.render(context)
                else:
                    msg = f"No template loader has been specified. "
                    msg += f"A template loader is required by the 'include' tag in "
                    msg += f"template '{self.token.template_id}', line {self.token.line_number}."
                    raise errors.TemplateLoadError(msg)
            else:
                msg = f"Invalid argument for the 'include' tag in template '{self.token.template_id}', "
                msg += f"line {self.token.line_number}. The variable '{self.arg}' should evaluate "
                msg += f"to a string. This variable has the value: {repr(template_name)}."
                raise errors.TemplateRenderingError(msg, self.token)


# ExtendNodes implement template inheritance. They indicate that the current template inherits
# from or 'extends' the specified parent template.
#
#     {% extends "parent.txt" %}
#
# Requires a template name to pass to the registered template loader. This must be supplied as a
# string literal (not a variable) as the parent template must be loaded at compile-time.
@register('extends')
class ExtendsNode(Node):

    def process_token(self, token):
        try:
            tag, arg = token.text.split(None, 1)
        except:
            msg = f"Malformed 'extends' tag in template '{token.template_id}', "
            msg += f"line {token.line_number}."
            raise errors.TemplateSyntaxError(msg, token) from None
        expr = Expression(arg, token)

        if expr.is_literal and isinstance(expr.literal, str):
            if ibis.loader:
                template = ibis.loader(expr.literal)
                self.children.append(template.root_node)
            else:
                msg = "No template loader has been specified. "
                msg += "A template loader is required by the 'extends' tag in "
                msg += "template '{token.template_id}', line {token.line_number}."
                raise errors.TemplateLoadError(msg)
        else:
            msg = f"Malformed 'extends' tag in template '{token.template_id}', "
            msg += f"line {token.line_number}. The template name must be a string literal."
            raise errors.TemplateSyntaxError(msg, token)


# BlockNodes implement template inheritance.
#
#    {% block title %} ... {% endblock %}
#
# A block tag defines a titled block of content that can be overridden by similarly titled blocks
# in child templates.
@register('block', 'endblock')
class BlockNode(Node):

    def process_token(self, token):
        self.title = token.text[5:].strip()

    def wrender(self, context):
        # We only want to render the first block of any given title that we encounter
        # in the node tree, although we want to substitute the content of the last
        # block of that title in its place.
        block_list = context.template.block_registry[self.title]
        if block_list[0] is self:
            return self.render_block(context, block_list[:])
        else:
            return ''

    def render_block(self, context, block_list):
        # A call to {{ super }} inside a block renders and returns the content of the
        # block's immediate ancestor. That ancestor may itself contain a {{ super }}
        # call, so we start at the end of the list and recursively work our way
        # backwards, popping off nodes as we go.
        if block_list:
            last_block = block_list.pop()
            context.push()
            context['super'] = lambda: self.render_block(context, block_list)
            output = ''.join(child.render(context) for child in last_block.children)
            context.pop()
            return output
        else:
            return ''


# Strips all whitespace between HTML tags.
@register('spaceless', 'endspaceless')
class SpacelessNode(Node):

    def wrender(self, context):
        output = ''.join(child.render(context) for child in self.children)
        return filters.filtermap['spaceless'](output).strip()


# Trims leading and trailing whitespace.
@register('trim', 'endtrim')
class TrimNode(Node):

    def wrender(self, context):
        return ''.join(child.render(context) for child in self.children).strip()


# Caches a complex expression under a simpler alias.
#
#    {% with <alias> = <expr> %} ... {% endwith %}
#
@register('with', 'endwith')
class WithNode(Node):

    def process_token(self, token):
        try:
            alias, expr = token.text[4:].split('=', 1)
        except:
            msg = f"Malformed 'with' tag in template '{token.template_id}', "
            msg += f"line {token.line_number}."
            raise errors.TemplateSyntaxError(msg, token) from None
        self.alias = alias.strip()
        self.expr = Expression(expr.strip(), token)

    def wrender(self, context):
        context.push()
        context[self.alias] = self.expr.eval(context)
        rendered = ''.join(child.render(context) for child in self.children)
        context.pop()
        return rendered

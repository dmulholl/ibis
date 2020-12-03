# --------------------------------------------------------------------------------------------------
# Ibis: a lightweight template engine.
#
# How it works: A lexer transforms a template string into a sequence of tokens. A parser takes this
# sequence and compiles it into a tree of nodes. Each node has a .render() method which takes a
# context object and returns a string. The entire compiled node tree can be rendered by calling
# .render() on the root node.
#
# Compiling and rendering the node tree are two distinct processes. The template only needs to be
# compiled once, it can then be cached and rendered multiple times with different context objects.
#
# The Template class acts as the public interface to the template engine. This is the only class
# the end-user needs to interact with directly. A Template object is initialized with a template
# string. It compiles the string and stores the resulting node tree for future rendering. Calling
# the template object's .render() method with a dictionary of key-value pairs or a set of keyword
# arguments renders the template and returns the result as a string.
#
# Example:
#
#     >>> template = Template('{{foo}} and {{bar}}')
#
#     >>> template.render(foo='ham', bar='eggs')
#     'ham and eggs'
#
#     >>> template.render({'foo': 1, 'bar': 2})
#     '1 and 2'
#
# --------------------------------------------------------------------------------------------------

from . import filters
from . import nodes
from . import loaders
from . import errors
from . import compiler

from .template import Template


# Library version.
__version__ = "2.0.0-alpha.1"


# Assign a template-loading callable here to enable the {% include %} and {% extends %} tags.
# The callable should accept one or more string arguments and either return an instance of the
# Template class or raise a TemplateLoadError exception.
loader = None

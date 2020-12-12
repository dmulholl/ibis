from . import filters
from . import nodes
from . import loaders
from . import errors
from . import compiler

from .template import Template


# Library version.
__version__ = "2.0.0-rc3"


# Assign a template-loading callable here to enable the {% include %} and {% extends %} tags.
# The callable should accept one or more string arguments and either return an instance of the
# Template class or raise a TemplateLoadError exception.
loader = None

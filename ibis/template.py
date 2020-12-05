from . import nodes
from . import compiler
from . import context


# A Template object is initialized with a template string containing template markup and a
# template ID which is used to identify the template in error messages. The .render() method
# accepts a data dictionary or a set of keyword arguments and returns a rendered output string.
#
# The ._register_blocks() method walks the node tree and assembles a dictionary containing lists
# of {% block %} nodes indexed by title. These lists are used to implement template inheritance -
# a block node occurring later in a list overrides those occuring earlier. (Note that we don't
# implement template inheritance by modifying the block nodes in situ. This is because templates
# can incorporate multiple (possibly-cached) sub-templates, so a single block node instance can
# form part of multiple distinct template trees.)
class Template:

    def __init__(self, template_string, template_id="UNIDENTIFIED"):
        self.root_node = compiler.compile(template_string, template_id)
        self.block_registry = self._register_blocks(self.root_node, {})

    def __str__(self):
        return str(self.root_node)

    def render(self, *pargs, **kwargs):
        data_dict = pargs[0] if pargs else kwargs
        strict_mode = kwargs.get("strict_mode", False)
        return self.root_node.render(context.Context(data_dict, self, strict_mode))

    def _register_blocks(self, node, registry):
        if isinstance(node, nodes.BlockNode):
            registry.setdefault(node.title, []).append(node)
        for child in node.children:
            self._register_blocks(child, registry)
        return registry


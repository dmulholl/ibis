import os

from .template import Template
from .errors import TemplateLoadError


# Loads templates from the file system. Assumes files are utf-8 encoded. Compiled templates are
# cached in memory, so they only need to be compiled once. Templates are *not* automatically
# recompiled if the underlying template file changes.
#
# A FileLoader instance should be initialized with a path to a base template directory.
#
#     loader = FileLoader('/path/to/base/directory')
#
# The loader instance can then be called with one or more path strings. The loader will return the
# template object corresponding to the first existing template file or raise a TemplateLoadError
# if no file can be located. Note that the path strings may include subdirectory paths:
#
#     template = loader('foo.txt')
#     template = loader('subdir/foo.txt')
#
class FileLoader:

    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.cache = {}

    def __call__(self, *filenames):
        for filename in filenames:
            if filename in self.cache:
                return self.cache[filename]

            path = os.path.join(self.root_dir, filename)
            if os.path.isfile(path):
                try:
                    with open(path, encoding='utf-8') as file:
                        template_string = file.read()
                except OSError as err:
                    msg = f"FileLoader cannot load the template file '{filename}'."
                    raise TemplateLoadError(msg) from err

                template = Template(template_string, filename)
                self.cache[filename] = template
                return template

        msg = f"FileLoader cannot find a template file matching the list {filenames}."
        raise TemplateLoadError(msg)


# Loads templates from the file system. Assumes files are utf-8 encoded. Compiled templates are
# cached in memory, so they only need to be compiled once. Templates are automatically recompiled
# if the underlying template file changes.
class FileReloader:

    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.cache = {}

    def __call__(self, *filenames):
        for filename in filenames:

            path = os.path.join(self.root_dir, filename)
            if os.path.isfile(path):
                mtime = os.path.getmtime(path)
                if filename in self.cache:
                    if mtime == self.cache[filename][0]:
                        return self.cache[filename][1]

                try:
                    with open(path, encoding='utf-8') as file:
                        template_string = file.read()
                except OSError as err:
                    msg = f"FileReloader cannot load the template file '{filename}'."
                    raise TemplateLoadError(msg) from err

                template = Template(template_string, filename)
                self.cache[filename] = (mtime, template)
                return template

        msg = f"FileReloader cannot find a template file matching the list {filenames}."
        raise TemplateLoadError(msg)


# Loads templates from a dictionary of template strings. Templates are compiled once and
# cached for future use.
class DictLoader:

    def __init__(self, template_strings):
        self.templates = {}
        self.template_strings = template_strings

    def __call__(self, *names):
        for name in names:
            if name in self.templates:
                return self.templates[name]
            elif name in self.template_strings:
                template = Template(self.template_strings[name], name)
                self.templates[name] = template
                return template
        msg = f"DictLoader has no entry matching the list {names}."
        raise TemplateLoadError(msg)

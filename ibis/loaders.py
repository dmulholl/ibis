
""" Default template loaders. """

import os

from .templates import Template
from .errors import LoadError


class FileLoader:

    """ Loads templates from the file system.

    Assumes template files are utf-8 encoded.

    Caches compiled template objects in memory. Automatically reloads
    if the underlying template file changes.

    Should be initialized with the path to the base template directory:

        loader = FileLoader('/path/to/base/directory')

    Template ID strings may include subdirectory paths:

        template = loader('foo.txt')
        template = loader('subdir/foo.txt')

    """

    def __init__(self, dirpath):
        self.dirpath = dirpath
        self.cache = {}

    def __call__(self, id):
        path = os.path.join(self.dirpath, id)

        try:
            mtime = os.path.getmtime(path)
            if id in self.cache:
                if mtime == self.cache[id][0]:
                    return self.cache[id][1]
            with open(path, encoding='utf-8') as tfile:
                tstring = tfile.read()
        except OSError:
            raise LoadError("error loading template file [%s]" % id)

        tobj = Template(tstring)
        self.cache[id] = (mtime, tobj)
        return tobj


class FastFileLoader(FileLoader):

    """ File system loader with no automatic reloading. """

    def __call__(self, id):
        if id in self.cache:
            return self.cache[id]

        path = os.path.join(self.dirpath, id)

        try:
            with open(path, encoding='utf-8') as tfile:
                tstring = tfile.read()
        except OSError:
            raise LoadError("error loading template file [%s]" % id)

        tobj = Template(tstring)
        self.cache[id] = tobj
        return tobj


class DictLoader:

    """ Loads templates from a dictionary of template strings. """

    def __init__(self, strings):
        self.templates = {}
        self.strings = strings

    def __call__(self, id):
        if id in self.templates:
            return self.templates[id]
        elif id in self.strings:
            template = Template(self.strings[id])
            self.templates[id] = template
            return template
        else:
            raise LoadError("no template matching [%s]" % id)

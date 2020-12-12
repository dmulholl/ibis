#!/usr/bin/env python3
"""
Ibis
====

Features:

* Django/Jinja-style syntax.
* Supports looping, conditionals, filters, template inheritance.
* Extensible. Easily add custom template tags and filters.
* Self-contained, no dependencies. Use as a drop-in component in any project.
* Public domain code. No license compatibility issues.

Sample syntax::

    <ul>
        {% for post in posts %}
            <li><a href="{{ post.url }}">{{ post.title }}</a></li>
        {% endfor %}
    </ul>

See the `package documentation <http://www.dmulholl.com/docs/ibis/master/>`_ or the
project's `Github homepage <https://github.com/dmulholl/ibis>`_ for
further details.

"""

import os
import re
import io

from setuptools import setup, find_packages


filepath = os.path.join(os.path.dirname(__file__), 'ibis', '__init__.py')
with io.open(filepath, encoding='utf-8') as metafile:
    regex = r'''^__([a-z]+)__ = ["'](.*)["']'''
    meta = dict(re.findall(regex, metafile.read(), flags=re.MULTILINE))


setup(
    name = 'ibis',
    version = meta['version'],
    packages =  find_packages(),
    include_package_data = True,
    python_requires = '>=3.6',
    author = 'Darren Mulholland',
    url='https://github.com/dmulholl/ibis',
    license = 'Public Domain',
    description = 'A lightweight template engine.',
    long_description = __doc__,
    classifiers = [
        'Programming Language :: Python :: 3',
        'Development Status :: 5 - Production/Stable',
        'Operating System :: OS Independent',
        'License :: Public Domain',
        'Intended Audience :: Developers',
        'Topic :: Text Processing :: General',
        'Topic :: Text Processing :: Markup :: HTML',
    ],
)

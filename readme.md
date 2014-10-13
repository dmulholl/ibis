
Flock
=====

A lightweight template engine in Python. Can be used as a drop-in component in text-processing applications.

Sample syntax:

    <ul>
        {% for post in posts %}
            <li><a href="{{ post.url }}">{{ post.title }}</a></li>
        {% endfor %}
    </ul>

Features:

* Django/Jinja-style syntax.
* Supports looping, conditionals, filters, template inheritance.
* Extensible. Easily add custom template tags and filters.
* Self-contained, no dependencies. Use as a drop-in component in any project.
* Public domain code. No license compatibility issues.


Quickstart
----------

Create a template object from a string:

    >>> import flock
    >>> template = flock.Template('{{foo}} and {{bar}}')

The template can be rendered multiple times by calling its `render()` method with a dictionary of key-value pairs or a set of keyword arguments:

    >>> template.render(foo='ham', bar='eggs')
    'ham and eggs'

    >>> template.render({'foo': 1, 'bar': 2})
    '1 and 2'


Requirements
------------

Requires Python 3.


License
-------

This work has been placed in the public domain.

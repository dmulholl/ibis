
Ibis
====

A lightweight template engine in Python.

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

    >>> import ibis
    >>> template = ibis.Template('{{foo}} and {{bar}}')

The template can be rendered multiple times by calling its `render()` method with a dictionary of key-value pairs or a set of keyword arguments:

    >>> template.render(foo='ham', bar='eggs')
    'ham and eggs'

    >>> template.render({'foo': 1, 'bar': 2})
    '1 and 2'

See the package's [documentation](http://pythonhosted.org/ibis) for further details.


Installation
------------

Install directly from the Python Package Index using `pip`:

    $ pip install ibis

Ibis requires Python 3.


License
-------

This work has been placed in the public domain.

# Ibis

[docs]: http://www.dmulholl.com/docs/ibis/master/
[jinja]: https://palletsprojects.com/p/jinja/

Ibis is a lightweight template engine for Python.

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
* Self-contained, no dependencies.
* Public domain code.

Ibis isn't intended to be [comprehensive][jinja] or to handle every possible use case for a template
engine &mdash; instead it's intended to be simple, robust, and pleasant to use.

See the [documentation][docs] for details.


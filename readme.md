# Ibis

[docs]: http://www.dmulholl.com/docs/ibis/master/

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

See the [documentation][docs] for details.



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

See the [documentation][] for details.

[docs]: http://mulholland.xyz/docs/ibis/

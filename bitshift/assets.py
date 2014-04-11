"""
:synopsis: Helper functions for use inside the project's Jinja templates.
"""

from flask import Markup

ASSET_HTML_TEMPLATES = {
    'css': "<link rel='stylesheet' type='text/css' href='/static/css/%s'>",
    'js': "<script src='/static/js/%s'></script>"
}

def tag(filename):
    """
    Generate an HTML tag for a CSS/JS asset, based on its file extension.

    :param filename: The filename of the asset to create a tag for.

    :return: A string containing a `<source>` tag for JS files, and a `<link>`
        for CSS files.
    """

    file_ext = filename.split(".")[-1]
    return Markup(ASSET_HTML_TEMPLATES[file_ext] % filename)

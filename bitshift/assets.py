"""
:synopsis: Helper functions for use inside the project's Jinja templates.
"""

from flask import Markup

ASSET_HTML_TEMPLATES = {
    'css': "<link rel='stylesheet' type='text/css' href='/css/%s'>",
    'js': "<script src='/js/%s'></script>"
}

def tag(filename):
    """
    Generate an HTML tag for a CSS/JS asset, based on its file extension.

    :param filename: The filename of the asset to create a tag for.

    :type filename: str

    :return: A string containing a `<source>` tag for JS files, and a `<link>`
        for CSS files.
    :rtype: str
    """

    file_ext = filename.split(".")[-1]
    return Markup(ASSET_HTML_TEMPLATES[file_ext] % filename)

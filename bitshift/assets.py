"""
Module contains helper functions to be used inside the project's Jinja
templates.
"""

from flask import Markup

ASSET_HTML_TEMPLATES = {
    'css': "<link rel='stylesheet' type='text/css' href='/static/css/%s'>",
    'js': "<script src='/static/js/%s'></script>"
}

def tag(filename):
    """
    Return HTML tag for asset named filename.

    Return either a <script> or <link> tag to the file named filename,
    based on its extension.
    """

    file_ext = filename.split(".")[-1]
    return Markup(ASSET_HTML_TEMPLATES[file_ext] % filename)

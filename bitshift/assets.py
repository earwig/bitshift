"""
:synopsis: Helper functions for use inside the project's Jinja templates.
"""

import re

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

def syntax_highlight(msg):
    """
    Inserts HTML `<span>` elements into a string, for symbol/word styling.

    Args:
        msg : (str) A message.
    """

    msg.replace("<", "&;lt")
    msg.replace(">", "&;gt")

    font_size = 16.0 / len(msg)
    msg = re.sub('([!()"%])', '<span class="dark">\\1</span>', msg)
    msg = re.sub('([:.;,])', '<span class="red">\\1</span>', msg)
    msg = msg.replace("404", '<span class="red">404</span>')
    return "<span class='light' style='font-size: %fem'>%s</span>" % (
            font_size, msg)

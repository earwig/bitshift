from operator import concat

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters.html import HtmlFormatter

from .languages import LANGS

__all__ = ["Codelet"]

class Codelet(object):
    """
    A source-code object with code metadata and composition analysis.

    :ivar name: (str) A suitable name for the codelet.
    :ivar code: (str) A containing the raw source code.
    :ivar filename: (str, or None) The filename of the snippet.
    :ivar language: (int, or None) The inferred language of `code`.
    :ivar authors: (array of tuples (str, str or None)) An array of tuples
        containing an author's name and profile URL (on the service the code
        was pulled from).
    :ivar url: (str) The url of the (page containing the) source code.
    :ivar date_created: (:class:`datetime.datetime`, or None) The date the code
        was published.
    :ivar date_modified: (:class:`datetime.datetime`, or None) The date the
        code was last modified.
    :ivar rank: (float) A quanitification of the source code's quality, as
        per available ratings (stars, forks, upvotes, etc.).
    :ivar symbols: (dict) Dictionary containing dictionaries of functions,
        classes, variable definitions, etc.
    :ivar origin: (tuple) 3-tuple of (site_name, site_url, image_blob), as
        added by the database.
    """

    def __init__(self, name, code, filename, language, authors, url,
                 date_created, date_modified, rank, symbols=None, origin=None):
        """
        Create a Codelet instance.

        :param name: see :attr:`self.name`
        :param code: see :attr:`self.code`
        :param filename: see :attr:`self.filename`
        :param language: see :attr:`self.language`
        :param authors: see :attr:`self.authors`
        :param url: see :attr:`self.url`
        :param date_created: see :attr:`self.date_created`
        :param date_modified: see :attr:`self.date_modified`
        :param rank: see :attr:`self.rank`
        :param symbols: see :attr:`self.symbols`
        :param origin: see :attr:`self.origin`

        :type name: see :attr:`self.name`
        :type code: see :attr:`self.code`
        :type filename: see :attr:`self.filename`
        :type language: see :attr:`self.language`
        :type authors: see :attr:`self.authors`
        :type url: see :attr:`self.url`
        :type date_created: see :attr:`self.date_created`
        :type date_modified: see :attr:`self.date_modified`
        :type rank: see :attr:`self.rank`
        :type symbols: see :attr:`self.symbols`
        :type origin: see :attr:`self.origin`
        """

        self.name = name
        self.code = code
        self.filename = filename
        self.language = language
        self.authors = authors
        self.url = url
        self.date_created = date_created
        self.date_modified = date_modified
        self.rank = rank
        self.symbols = symbols or {}
        self.origin = origin or (None, None, None)

    def serialize(self):
        """
        Convert the codelet into a dictionary that can be sent as JSON.

        :return: The codelet as a dictionary.
        :rtype: str
        """
        lang = LANGS[self.language]
        lines = reduce(concat, [[loc[0] for loc in sym[1] + sym[2]] for sym in
                                reduce(concat, self.symbols.values())])
        formatter = HtmlFormatter(linenos=True, hl_lines=lines)
        code = highlight(self.code, get_lexer_by_name(lang.lower()), formatter)

        return {
            "name": self.name, "code": code, "lang": lang,
            "authors": self.authors, "url": self.url,
            "created": self.date_created.isoformat(),
            "modified": self.date_modified.isoformat(), "origin": self.origin
        }

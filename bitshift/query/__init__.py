"""
This subpackage contains code to parse search queries received from the
frontend into trees that can be used by the database backend.
"""

from shlex import split

from .nodes import *  ## TODO
from .tree import Tree
from ..languages import LANGS

__all__ = ["QueryParseException", "parse_query"]

class QueryParseException(Exception):
    """Raised by parse_query() when a query is invalid."""
    pass

class _QueryParser(object):
    """Wrapper class with methods to parse queries. Used as a singleton."""

    def __init__(self):
        prefixes = {
            "language": _parse_language,
            "author": _parse_author,
            "modified": _parse_modified,
            "created": _parse_created,
            "symbol": _parse_symbol,
            "function": _parse_function,
            "class": _parse_class,
            "variable": _parse_variable
        }

    def _parse_language(self, term):
        pass

    def _parse_author(self, term):
        pass

    def _parse_modified(self, term):
        pass

    def _parse_created(self, term):
        pass

    def _parse_symbol(self, term):
        pass

    def _parse_function(self, term):
        pass

    def _parse_class(self, term):
        pass

    def _parse_variable(self, term):
        pass

    def parse(self, query):
        """
        Parse a search query.

        The result is normalized with a sorting function so that ``"foo OR bar"``
        and ``"bar OR foo"`` result in the same tree. This is important for caching
        purposes.

        :param query: The query be converted.
        :type query: str

        :return: A tree storing the data in the query.
        :rtype: :py:class:`~.query.tree.Tree`

        :raises: :py:class:`.QueryParseException`
        """
        for term in split(query):
            if ":" in term and not term[0] == ":":
                prefix = term.split(":")[0]



        # language:"Python"
        # lang:
        # l:

        # author:"Ben Kurtovic"

        # modified:before
        # modified:after
        # created:before
        # created:after:"Jaunary 4, 2014"

        # func:"foobar"
        # func:re|gex:"foo?b|car"

        # "foo" -> Tree()
        # "foo bar" -> "foo bar" OR ("foo" or "bar")
        # "foo bar baz" -> ""foo bar baz" OR ("foo" OR "bar baz") OR ("foo" OR "bar baz") OR ('foo' OR 'bar' OR 'baz')"


parse_query = _QueryParser().parse

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
        self._prefixes = {
            self._parse_language: ["l", "lang", "language"],
            self._parse_author: ["a", "author"],
            self._parse_modified: ["m", "mod", "modified", "modify"],
            self._parse_created: ["cr", "create", "created"],
            self._parse_symbol: ["s", "sym", "symb", "symbol"],
            self._parse_function: ["f", "fn", "func", "function"],
            self._parse_class: ["cl", "class", "clss"],
            self._parse_variable: ["v", "var", "variable"]
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

    def _parse_literal(self, literal):
        """Parse part of a search query into a string or regular expression."""
        if literal.startswith(("r:", "re:", "regex:", "regexp:")):
            return Regex(literal.split(":", 1)[1])
        return String(literal)

    def _parse_term(self, term):
        """Parse a query term into a tree node and return it."""
        if ":" in term and not term[0] == ":":
            prefix, arg = term.split(":", 1)
            for meth, prefixes in self._prefixes.iteritems():
                if prefix in prefixes:
                    return meth(arg)
        return Text(self._parse_literal(term))

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
        print "input:", query
        for term in split(query):
            print "term: ", term
            node = self._parse_term(term)
            print "parse:", node
            tree = Tree(node)
            print "tree: ", tree
            return tree
            ## TODO

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

"""
This subpackage contains code to parse search queries received from the
frontend into trees that can be used by the database backend.
"""

from __future__ import unicode_literals
from re import IGNORECASE, search
from shlex import split

from dateutil.parser import parse as parse_date

from .nodes import (String, Regex, Text, Language, Author, Date, Symbol,
                    BinaryOp, UnaryOp)
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

    def _parse_literal(self, literal):
        """Parse part of a search query into a string or regular expression."""
        if literal.startswith(("r:", "re:", "regex:", "regexp:")):
            return Regex(literal.split(":", 1)[1])
        return String(literal)

    def _parse_language(self, term):
        """Parse part of a query into a language node and return it."""
        term = self._parse_literal(term)
        if isinstance(term, Regex):
            langs = [i for i, lang in enumerate(LANGS)
                     if search(term.regex, lang, IGNORECASE)]
            if not langs:
                err = 'No languages found for regex: "%s"' % term.regex
                raise QueryParseException(err)
            node = Language(langs.pop())
            while langs:
                node = BinaryOp(Language(langs.pop()), BinaryOp.OR, node)
            return node

        needle = term.string.lower()
        for i, lang in enumerate(LANGS):
            if lang.lower() == needle:
                return Language(i)
        for i, lang in enumerate(LANGS):
            if lang.lower().startswith(needle):
                return Language(i)
        err = 'No languages found for string: "%s"' % term.string
        raise QueryParseException(err)

    def _parse_author(self, term):
        """Parse part of a query into an author node and return it."""
        return Author(self._parse_literal(term))

    def _parse_date(self, term, type_):
        """Parse part of a query into a date node and return it."""
        if ":" not in term:
            err = "A date relationship is required " \
                  '("before:<date>" or "after:<date>"): "%s"'
            raise QueryParseException(err % term)
        relstr, dtstr = term.split(":", 1)
        if relstr.lower() in ("before", "b"):
            relation = Date.BEFORE
        elif relstr.lower() in ("after", "a"):
            relation = Date.AFTER
        else:
            err = 'Bad date relationship (should be "before" or "after"): "%s"'
            raise QueryParseException(err % relstr)
        try:
            dt = parse_date(dtstr)
        except (TypeError, ValueError):
            raise QueryParseException('Bad date/time string: "%s"' % dtstr)
        return Date(type_, relation, dt)

    def _parse_modified(self, term):
        """Parse part of a query into a date modified node and return it."""
        return self._parse_date(term, Date.MODIFY)

    def _parse_created(self, term):
        """Parse part of a query into a date created node and return it."""
        return self._parse_date(term, Date.CREATE)

    def _parse_symbol(self, term):
        """Parse part of a query into a symbol node and return it."""
        return Symbol(Symbol.ALL, self._parse_literal(term))

    def _parse_function(self, term):
        """Parse part of a query into a function node and return it."""
        return Symbol(Symbol.FUNCTION, self._parse_literal(term))

    def _parse_class(self, term):
        """Parse part of a query into a class node and return it."""
        return Symbol(Symbol.CLASS, self._parse_literal(term))

    def _parse_variable(self, term):
        """Parse part of a query into a variable node and return it."""
        return Symbol(Symbol.VARIABLE, self._parse_literal(term))

    def _parse_term(self, term):
        """Parse a query term into a tree node and return it."""
        if ":" in term and not term[0] == ":":
            prefix, arg = term.split(":", 1)
            invert = prefix.lower() == "not"
            if invert:
                prefix, arg = arg.split(":", 1)
            if not arg:
                raise QueryParseException('Incomplete query term: "%s"' % term)
            for meth, prefixes in self._prefixes.iteritems():
                if prefix.lower() in prefixes:
                    if invert:
                        return UnaryOp(UnaryOp.NOT, meth(arg))
                    return meth(arg)
        return Text(self._parse_literal(term))

    def parse(self, query):
        """
        Parse a search query.

        The result is normalized with a sorting function so that
        ``"foo OR bar"`` and ``"bar OR foo"`` result in the same tree. This is
        important for caching purposes.

        :param query: The query be converted.
        :type query: str

        :return: A tree storing the data in the query.
        :rtype: :py:class:`~.query.tree.Tree`

        :raises: :py:class:`.QueryParseException`
        """
        root = None
        for term in split(query):
            node = self._parse_term(term)
            root = BinaryOp(root, BinaryOp.AND, node) if root else node
        tree = Tree(root)
        return tree


parse_query = _QueryParser().parse

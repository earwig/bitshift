"""
This subpackage contains code to parse search queries received from the
frontend into trees that can be used by the database backend.
"""

from __future__ import unicode_literals
from re import IGNORECASE, search
from sys import maxsize

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
            self._parse_function: ["f", "fn", "fun", "func", "function"],
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
        try:
            term = term.decode("unicode_escape")
        except UnicodeDecodeError:
            raise QueryParseException('Invalid query term: "%s"' % term)
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

    def _scan_query(self, query, markers):
        """Scan a query (sub)string for the first occurance of some markers.

        Returns a 2-tuple of (first_marker_found, marker_index).
        """
        def _is_escaped(query, index):
            """Return whether a query marker is backslash-escaped."""
            return (index > 0 and query[index - 1] == "\\" and
                    (index < 2 or query[index - 2] != "\\"))

        best_marker, best_index = None, maxsize
        for marker in markers:
            index = query.find(marker)
            if _is_escaped(query, index):
                _, new_index = self._scan_query(query[index + 1:], marker)
                index += new_index + 1
            if index >= 0 and index < best_index:
                best_marker, best_index = marker, index
        return best_marker, best_index

    def _split_query(self, query, parens=False):
        """Split a query string into a nested list of query terms.

        Returns a list of terms and/or nested sublists of terms. Each term and
        sublist is guarenteed to be non-empty.
        """
        query = query.lstrip()
        if not query:
            return []
        marker, index = self._scan_query(query, " \"'()")
        if not marker:
            return [query]
        nest = [query[:index]] if index > 0 else []
        after = query[index + 1:]

        if marker == " ":
            nest += self._split_query(after, parens)
        elif marker in ('"', "'"):
            close_marker, close_index = self._scan_query(after, marker)
            if close_marker:
                if close_index > 0:
                    nest.append(after[:close_index])
                after = after[close_index + 1:]
                nest += self._split_query(after, parens)
            elif after:
                nest.append(after)
        elif marker == "(":
            inner, after = self._split_query(after, True), []
            if inner and isinstance(inner[-1], tuple):
                after = self._split_query(inner.pop()[0], parens)
            if inner:
                nest.append(inner)
            if after:
                nest += after
        elif marker == ")":
            if parens:
                nest.append((after,))
            else:
                nest += self._split_query(after)
        return nest

    def _parse_boolean_operators(self, nest):
        """Parse boolean operators in a nested query list."""
        op_lookup = {
            "and": BinaryOp.AND,
            "or": BinaryOp.OR,
            "not": UnaryOp.NOT
        }
        for i, term in enumerate(nest):
            if isinstance(term, list):
                self._parse_boolean_operators(term)
            else:
                nest[i] = op_lookup.get(term.lower(), term)

    def _parse_nest(self, nest):
        """Recursively parse a nested list of search query terms."""
        def parse_binary_op(op):
            """Parse a binary operator in a nested query list."""
            index = nest.index(op)
            if index == 0 or index == len(nest) - 1:
                err = "Invalid query: '%s' given without argument."
                raise QueryParseException(err % BinaryOp.OPS[op])
            left = self._parse_nest(nest[:index])
            right = self._parse_nest(nest[index + 1:])
            return BinaryOp(left, op, right)

        if not nest:
            err = "Error while parsing query: empty nest detected."
            raise QueryParseException(err)
        elif BinaryOp.OR in nest:
            return parse_binary_op(BinaryOp.OR)
        elif BinaryOp.AND in nest:
            return parse_binary_op(BinaryOp.AND)
        elif UnaryOp.NOT in nest:
            index = nest.index(UnaryOp.NOT)
            if index == len(nest) - 1:
                err = "Invalid query: '%s' given without argument."
                raise QueryParseException(err % UnaryOp.OPS[op])
            right = UnaryOp(UnaryOp.NOT, self._parse_nest(nest[index + 1:]))
            if index > 0:
                left = self._parse_nest(nest[:index])
                return BinaryOp(left, BinaryOp.AND, right)
            return right
        elif len(nest) > 1:
            left, right = self._parse_term(nest[0]), self._parse_nest(nest[1:])
            return BinaryOp(left, BinaryOp.AND, right)
        elif isinstance(nest[0], list):
            return self._parse_nest(nest[0])
        else:
            return self._parse_term(nest[0])

    def _balance_tree(self, node):
        """Auto-balance a tree using a string sorting function."""
        if isinstance(node, BinaryOp):
            self._balance_tree(node.left)
            self._balance_tree(node.right)
            if node.right.sortkey() < node.left.sortkey():
                node.left, node.right = node.right, node.left
        elif isinstance(node, UnaryOp):
            self._balance_tree(node.node)

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
        nest = self._split_query(query.rstrip())
        if not nest:
            raise QueryParseException('Empty query: "%s"' % query)
        self._parse_boolean_operators(nest)
        root = self._parse_nest(nest)
        self._balance_tree(root)
        return Tree(root)


parse_query = _QueryParser().parse

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
        ## TODO: balance tree
        ## --------------------------------------------------------------------

        def SCAN_FOR_MARKER(string, markers):
            best_marker, best_index = None, maxsize
            for marker in markers:
                index = string.find(marker)
                if index > 0 and string[index - 1] == "\\" and (index == 1 or string[index - 2] != "\\"):
                    _, new_index = SCAN_FOR_MARKER(string[index + 1:], marker)
                    index += new_index + 1
                if index >= 0 and index < best_index:
                    best_marker, best_index = marker, index
            return best_marker, best_index

        def SPLIT_QUERY_STRING(string, parens=False):
            string = string.lstrip()
            if not string:
                return []
            marker, index = SCAN_FOR_MARKER(string, " \"'()")

            if not marker:
                return [string]

            before = [string[:index]] if index > 0 else []
            after = string[index + 1:]

            if marker == " ":
                return before + SPLIT_QUERY_STRING(after, parens)

            elif marker in ('"', "'"):
                close_marker, close_index = SCAN_FOR_MARKER(after, marker)
                if not close_marker:
                    return before + [after]
                quoted, after = after[:close_index], after[close_index + 1:]
                return before + [quoted] + SPLIT_QUERY_STRING(after, parens)

            elif marker == "(":
                inner = SPLIT_QUERY_STRING(after, True)
                if inner and isinstance(inner[-1], tuple):
                    after, inner = inner.pop()[0], [inner] if inner else []
                    return before + inner + SPLIT_QUERY_STRING(after, parens)
                return before + [inner]

            elif marker == ")":
                if parens:
                    return before + [(after,)]
                return before + SPLIT_QUERY_STRING(after)

        nest = SPLIT_QUERY_STRING(query.rstrip())
        if not nest:
            raise QueryParseException('Empty query: "%s"' % query)

        return nest

        ###########

        group = _NodeGroup()
        for term in split(query):

            while term.startswith("("):
                group = _NodeList(group, explicit=True)
                term = term[1:]

            closes = 0
            while term.endswith(")"):
                closes += 1
                term = term[:-1]

            if not term:
                for i in xrange(closes):
                    group = reduce_group(group, explicit=True)
                continue

            lcase = term.lower()

            if lcase == "not":
                UnaryOp.NOT
            elif lcase == "or":
                BinaryOp.OR
            elif lcase == "and":
                if group.pending_op:
                    pass
                else:
                    group.pending_op = BinaryOP.AND
            else:
                group.nodes.append(self._parse_term(term))

        return Tree(reduce_group(group, explicit=False))

        ## --------------------------------------------------------------------

        # root = None
        # for node in reversed(nodes):
        #     root = BinaryOp(node, BinaryOp.AND, root) if root else node
        # tree = Tree(root)
        # return tree

class _NodeGroup(object):
    def __init__(self, parent=None):
        self.parent = parent
        self.op = None
        self.left = None
        self.right = None


parse_query = _QueryParser().parse

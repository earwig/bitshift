# -*- coding: utf-8  -*-

from __future__ import unicode_literals
import unittest

from bitshift.query import parse_query

TESTS = [
    # Text
    ("test", "Tree(Text(String(u'test')))"),
    ("re:test", "Tree(Text(Regex(u'test')))"),

    # Language
    ("language:python", "Tree(Language(Python))"),
    ("language:py", "Tree(Language(Python))"),
    ("l:r:r..y", "Tree(Language(Ruby))"),
    (r'"lang:re:python|^c$"',
     "Tree(BinaryOp(Language(C), OR, Language(Python)))"),

    # Author
    ('"author:Ben Kurtovic"', "Tree(Author(String(u'Ben Kurtovic')))"),
    (r"'a:re:b.*?\sk.*?'", r"Tree(Author(Regex(u'b.*?\\sk.*?')))"),

    # Date
    ("'create:before:Jan 1, 2014'",
     "Tree(Date(CREATE, BEFORE, 2014-01-01 00:00:00))"),
    ("'modify:after:2010-05-09 10:11:12'",
     "Tree(Date(MODIFY, AFTER, 2010-05-09 10:11:12))"),

    # Symbol
    ("sym:foobar", "Tree(Symbol(ALL, ALL, String(u'foobar')))"),
    ("func:foo_bar", "Tree(Symbol(ALL, FUNCTION, String(u'foo_bar')))"),
    ("func:foo_bar()", "Tree(Symbol(ALL, FUNCTION, String(u'foo_bar')))"),
    ("class:FooBar", "Tree(Symbol(ALL, CLASS, String(u'FooBar')))"),
    ("var:foobar", "Tree(Symbol(ALL, VARIABLE, String(u'foobar')))"),
    ("var:r:foobar", "Tree(Symbol(ALL, VARIABLE, Regex(u'foobar')))"),

    # Composition
    ("(a and b) or (c and d)", ", ".join([
        "Tree(BinaryOp(BinaryOp(Text(String(u'a'))", "AND",
        "Text(String(u'b')))", "OR", "BinaryOp(Text(String(u'c'))", "AND",
        "Text(String(u'd')))))"])),
    ("a and b or c and d", ", ".join([
        "Tree(BinaryOp(BinaryOp(Text(String(u'a'))", "AND",
        "Text(String(u'b')))", "OR", "BinaryOp(Text(String(u'c'))", "AND",
        "Text(String(u'd')))))"])),
    ("a and b or c or d", ", ".join([
        "Tree(BinaryOp(BinaryOp(Text(String(u'a'))", "AND",
        "Text(String(u'b')))", "OR", "BinaryOp(Text(String(u'c'))", "OR",
        "Text(String(u'd')))))"])),
    ("a and (b or c or d)", ", ".join([
        "Tree(BinaryOp(Text(String(u'a'))", "AND",
        "BinaryOp(Text(String(u'b'))", "OR", "BinaryOp(Text(String(u'c'))", "OR",
        "Text(String(u'd'))))))"])),
    ("a not b", ", ".join([
        "Tree(BinaryOp(Text(String(u'a'))", "AND", "UnaryOp(NOT",
        "Text(String(u'b')))))"])),

    # Unicode, Escaping
    (r'lang:py "author:fo\\o \"bar\" baz\\"', ", ".join([
        "Tree(BinaryOp(Language(Python)", "AND",
        "Author(String(u'fo\\\\o \"bar\" baz\\\\'))))"])),
    ('"author:Ben Kurtović"', "Tree(Author(String(u'Ben Kurtovi\\u0107')))")
]

class TestQueryParser(unittest.TestCase):
    """Unit tests for the query parser in :py:mod:`bitshift.query`."""

    def test_parse(self):
        """test full query parsing"""
        for test, expected in TESTS:
            self.assertEqual(expected, parse_query(test).serialize())


if __name__ == "__main__":
    unittest.main(verbosity=2)

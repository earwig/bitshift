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
    ("lang:re:py|c", "Tree(BinaryOp(Language(C), OR, Language(Python)))"),

    # Author
    ('"author:Ben Kurtovic"', "Tree(Author(String(u'Ben Kurtovic')))"),
    (r"'a:re:b.*?\sk.*?'", r"Tree(Author(Regex(u'b.*?\\sk.*?')))"),

    # Date
    ("'create:before:Jan 1, 2014'",
     "Tree(Date(CREATE, BEFORE, 2014-01-01 00:00:00))"),
    ("'modify:after:2010-05-09 10:11:12'",
     "Tree(Date(MODIFY, AFTER, 2010-05-09 10:11:12))"),

    # Symbol
    ("sym:foobar", "Tree(Symbol(ALL, String(u'foobar')))"),
    ("func:foo_bar", "Tree(Symbol(FUNCTION, String(u'foo_bar')))"),
    ("func:foo_bar()", "Tree(Symbol(FUNCTION, String(u'foo_bar')))"),
    ("class:FooBar", "Tree(Symbol(CLASS, String(u'FooBar')))"),
    ("var:foobar", "Tree(Symbol(VARIABLE, String(u'foobar')))"),
    ("var:r:foobar", "Tree(Symbol(VARIABLE, Regex(u'foobar')))"),
]

class TestQueryParser(unittest.TestCase):
    """Unit tests for the query parser in :py:mod:`bitshift.query`."""

    def test_parse(self):
        """test full query parsing"""
        for test, expected in TESTS:
            self.assertEqual(expected, parse_query(test).serialize())


if __name__ == "__main__":
    unittest.main(verbosity=2)

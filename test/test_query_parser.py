from __future__ import unicode_literals
import unittest

from bitshift.query import parse_query

class TestQueryParser(unittest.TestCase):
    """Unit tests for the query parser in :py:mod:`bitshift.query`."""

    def test_parse(self):
        """test basic query parsing"""
        pq = lambda s: parse_query(s).serialize()
        self.assertEqual("Tree(Text(String('test')))", pq("test"))
        self.assertEqual("Tree(Text(Regex('test')))", pq("re:test"))


if __name__ == "__main__":
    unittest.main(verbosity=2)

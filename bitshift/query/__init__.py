from .nodes import *  ## TODO
from .tree import Tree

__all__ = ["QueryParseException", "parse_query"]

class QueryParseException(Exception):
    """Raised by parse_query when a query is invalid."""
    pass


def parse_query(query):
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
    for term in query.split(" "):
        pass

    language:"Python"
    lang:
    l:

    author:"Ben Kurtovic"

    modified:before
    modified:after
    created:before
    created:after:"Jaunary 4, 2014"

    func:"foobar"
    func:re|gex:"foo?b|car"

    # "foo" -> Tree()
    # "foo bar" -> "foo bar" OR ("foo" or "bar")
    # "foo bar baz" -> ""foo bar baz" OR ("foo" OR "bar baz") OR ("foo" OR "bar baz") OR ('foo' OR 'bar' OR 'baz')"

from .nodes import *  ## TODO
from .tree import Tree

__all__ = ["parse_query"]

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
    """
    pass

    # "foo" -> Tree()
    # "foo bar" -> "foo bar" OR ("foo" or "bar")
    # "foo bar baz" -> ""foo bar baz" OR ("foo" OR "bar baz") OR ("foo" OR "bar baz") OR ('foo' OR 'bar' OR 'baz')"

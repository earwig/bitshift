from .associations import BinaryOp, UnaryOp
from .node import Node
from .tree import Tree

__all__ = ["parse_query"]

def parse_query(query):
    """
    Parse a search query.

    :param query: The query be converted.
    :type query: str

    :return: A tree storing the data in the query.
    :rtype: :py:class:`~.query.tree.Tree`
    """




    "bubble sort lang:python"


    # gets a string, returns a Tree
    # TODO: note: resultant Trees should be normalized so that "foo OR bar"
    # and "bar OR foo" result in equivalent trees
    pass

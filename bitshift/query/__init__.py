from .association import Association
from .node import Node
from .tree import Tree

__all__ = ["parse_query"]

def parse_query(query):
    # gets a string, returns a Tree
    # TODO: note: resultant Trees should be normalized so that "foo OR bar"
    # and "bar OR foo" result in equivalent trees
    pass

__all__ = ["Node", "Text", "BinaryOp", "UnaryOp"]

class _Literal(object):
    """Represents a literal component of a search query, present at the leaves.

    A literal might be a string or a regular expression.
    """
    pass


class _String(_Literal)
    """Represents a string literal."""

    def __init__(self, string):
        self.string = string

    def __repr__(self):
        return "String({0!r})".format(self.string)


class _Regex(_Literal):
    """Represents a regular expression literal."""

    def __init__(self, regex):
        self.regex = regex

    def __repr__(self):
        return "Regex({0!r})".format(self.regex)


class Node(object):
    """Represents a single node in a query tree."""
    pass


class Text(Node):
    """Represents a text node.

    Searches in codelet names (full-text search), symbols (equality), and
    source code (full-text search).
    """

    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return "Text({0})".format(self.text)


# Language -> code_lang (direct)
# DateRange -> codelet_date_created (cmp), codelet_date_modified (cmp)
# Author -> author_name (FTS)
# Symbol -> func, class, var -> symbol_type, symbol_name (direct)


class BinaryOp(Node):
    """Represents a relationship between two nodes: ``and``, ``or``."""
    AND = 1
    OR = 2

    def __init__(self, left, right, op):
        self.left = left
        self.right = right
        self.op = op

    def __repr__(self):
        ops = {self.AND: "And", self.OR: "Or"}
        return "{0}({1}, {2})".format(ops[self.op], self.left, self.right)


class UnaryOp(Node):
    """Represents a transformation applied to one node: ``not``."""
    NOT = 1

    def __init__(self, node, op):
        self.node = node
        self.op = op

    def __repr__(self):
        ops = {self.NOT: "Not"}
        return "{0}({1})".format(ops[self.op], self.node)

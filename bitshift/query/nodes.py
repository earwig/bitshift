from ..languages import LANGS

__all__ = ["String", "Regex", "Text", "Language", "Author", "Date", "Symbol",
           "BinaryOp", "UnaryOp"]

class _Node(object):
    """Represents a single node in a query tree.

    Generally speaking, a node is a constraint applied to the database. Thus,
    a :py:class:`~.Language` node represents a constraint where only codelets
    of a specific language are selected.
    """
    pass


class _Literal(object):
    """Represents a literal component of a search query, present at the leaves.

    A literal might be a string or a regular expression.
    """
    pass


class String(_Literal):
    """Represents a string literal."""

    def __init__(self, string):
        """
        :type string: unicode
        """
        self.string = string

    def __repr__(self):
        return "String({0!r})".format(self.string)


class Regex(_Literal):
    """Represents a regular expression literal."""

    def __init__(self, regex):
        """
        :type string: unicode
        """
        self.regex = regex

    def __repr__(self):
        return "Regex({0!r})".format(self.regex)


class Text(_Node):
    """Represents a text node.

    Searches in codelet names (full-text search), symbols (equality), and
    source code (full-text search).
    """

    def __init__(self, text):
        """
        :type text: :py:class:`._Literal`
        """
        self.text = text

    def __repr__(self):
        return "Text({0})".format(self.text)


class Language(_Node):
    """Represents a language node.

    Searches in the code_lang field.
    """

    def __init__(self, lang):
        """
        :type lang: int
        """
        self.lang = lang

    def __repr__(self):
        return "Language({0})".format(LANGS[self.lang])


class Author(_Node):
    """Represents a author node.

    Searches in the author_name field (full-text search).
    """

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "Author({0})".format(self.name)


class Date(_Node):
    """Represents a date node.

    Searches in the codelet_date_created or codelet_date_modified fields.
    """
    CREATE = 1
    MODIFY = 2

    BEFORE = 1
    AFTER = 2

    def __init__(self, type_, relation, date):
        """
        :type type_: int (``CREATE`` or ``MODIFY``)
        :type relation: int (``BEFORE``, ``AFTER``)
        :type date: datetime.datetime
        """
        self.type = type_
        self.relation = relation
        self.date = date

    def __repr__(self):
        types = {self.CREATE: "CREATE", self.MODIFY: "MODIFY"}
        relations = {self.BEFORE: "BEFORE", self.AFTER: "AFTER"}
        tm = "Date({0}, {1}, {2})"
        return tm.format(types[self.type], relations[self.relation], self.date)


class Symbol(_Node):
    """Represents a symbol node.

    Searches in symbol_type and symbol_name.
    """
    ALL = 0
    FUNCTION = 1
    CLASS = 2
    VARIABLE = 3

    def __init__(self, type_, name):
        """
        :type type_: int (``ALL``, ``FUNCTION``, ``CLASS``, etc.)
        :type name: :py:class:`.Literal`
        """
        self.type = type_
        self.name = name

    def __repr__(self):
        types = {self.ALL: "ALL", self.FUNCTION: "FUNCTION",
                 self.CLASS: "CLASS", self.VARIABLE: "VARIABLE"}
        return "Symbol({0}, {1})".format(types[self.type], name)


class BinaryOp(_Node):
    """Represents a relationship between two nodes: ``and``, ``or``."""
    AND = 1
    OR = 2

    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self):
        ops = {self.AND: "AND", self.OR: "OR"}
        tmpl = "BinaryOp({0}, {1}, {2})"
        return tmpl.format(self.left, ops[self.op], self.right)


class UnaryOp(_Node):
    """Represents a transformation applied to one node: ``not``."""
    NOT = 1

    def __init__(self, op, node):
        self.op = op
        self.node = node

    def __repr__(self):
        ops = {self.NOT: "NOT"}
        return "UnaryOp({0}, {1})".format(ops[self.op], self.node)

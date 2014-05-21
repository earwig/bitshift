from ..languages import LANGS

__all__ = ["String", "Regex", "Text", "Language", "Author", "Date", "Symbol",
           "BinaryOp", "UnaryOp"]

class _Node(object):
    """Represents a single node in a query tree.

    Generally speaking, a node is a constraint applied to the database. Thus,
    a :py:class:`~.Language` node represents a constraint where only codelets
    of a specific language are selected.
    """

    def sortkey(self):
        """Return a string sort key for the node."""
        return ""

    def parameterize(self, tables):
        """Parameterize the node.

        Returns a 3-tuple of (conditional string, rank list, parameter list).
        If the rank list is empty, then it is assumed to contain the
        conditional string.
        """
        return "", [], []


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

    def sortkey(self):
        return self.string


class Regex(_Literal):
    """Represents a regular expression literal."""

    def __init__(self, regex):
        """
        :type string: unicode
        """
        self.regex = regex

    def __repr__(self):
        return "Regex({0!r})".format(self.regex)

    def sortkey(self):
        return self.regex


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

    def sortkey(self):
        return self.text.sortkey()

    def parameterize(self, tables):
        tables |= {"code", "symbols"}
        if isinstance(self.text, Regex):
            ranks = ["(codelet_name REGEXP ?)", "(symbol_name REGEXP ?)",
                     "(code_code REGEXP ?)"]
            text = self.text.regex
        else:
            ranks = ["(MATCH(codelet_name) AGAINST (? IN BOOLEAN MODE))",
                     "(MATCH(code_code) AGAINST (? IN BOOLEAN MODE))",
                     "(symbol_name = ?)"]
            text = self.text.string
        return cond, ranks, [text] * 3


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

    def sortkey(self):
        return LANGS[self.lang]

    def parameterize(self, tables):
        tables |= {"code"}
        return "(code_lang = ?)", [], [self.lang]


class Author(_Node):
    """Represents a author node.

    Searches in the author_name field (full-text search).
    """

    def __init__(self, name):
        """
        :type name: :py:class:`_Literal`
        """
        self.name = name

    def __repr__(self):
        return "Author({0})".format(self.name)

    def sortkey(self):
        return self.name.sortkey()

    def parameterize(self, tables):
        tables |= {"authors"}
        if isinstance(self.name, Regex):
            return "(author_name REGEXP ?)", [], [self.name.regex]
        cond = "(MATCH(author_name) AGAINST (? IN BOOLEAN MODE))"
        return cond, [], [self.name.string]


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

    def sortkey(self):
        return self.date.strftime("%Y%m%d%H%M%S")

    def parameterize(self, tables):
        column = {self.CREATE: "codelet_date_created",
                  self.MODIFY: "codelet_date_modified"}[self.type]
        op = {self.BEFORE: "<=", self.AFTER: ">="}[self.relation]
        return "(" + column + " " + op + " ?)", [], [self.date]


class Symbol(_Node):
    """Represents a symbol node.

    Searches in symbol_type and symbol_name.
    """
    ALL = 0
    FUNCTION = 1
    CLASS = 2
    VARIABLE = 3
    TYPES = {FUNCTION: "FUNCTION", CLASS: "CLASS", VARIABLE: "VARIABLE"}

    def __init__(self, type_, name):
        """
        :type type_: int (``ALL``, ``FUNCTION``, ``CLASS``, etc.)
        :type name: :py:class:`._Literal`
        """
        self.type = type_
        self.name = name

    def __repr__(self):
        type_ = self.TYPES.get(self.type, "ALL")
        return "Symbol({0}, {1})".format(type_, self.name)

    def sortkey(self):
        return self.name.sortkey()

    def parameterize(self, tables):
        tables |= {"code", "symbols"}
        if isinstance(self.name, Regex):
            cond_base = "(symbol_type = ? AND symbol_name REGEXP ?)"
            name = self.name.regex
        else:
            cond_base = "(symbol_type = ? AND symbol_name = ?)"
            name = self.name.string
        if self.type != self.ALL:
            return cond_base, [], [self.type, name]
        cond = "(" + " OR ".join([cond_base] * len(self.TYPES)) + ")"
        args = zip(self.TYPES.keys(), [name] * len(self.TYPES))
        return cond, [], [arg for tup in args for arg in tup]


class BinaryOp(_Node):
    """Represents a relationship between two nodes: ``and``, ``or``."""
    AND = object()
    OR = object()
    OPS = {AND: "AND", OR: "OR"}

    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self):
        tmpl = "BinaryOp({0}, {1}, {2})"
        return tmpl.format(self.left, self.OPS[self.op], self.right)

    def sortkey(self):
        return self.left.sortkey() + self.right.sortkey()

    def parameterize(self, tables):
        lcond, lranks, largs = self.left.parameterize(tables)
        rcond, rranks, rargs = self.right.parameterize(tables)
        lranks, rranks = lranks or [lcond], rranks or [rcond]
        op = self.OPS[self.op]
        cond = "(" + lcond  + " " + op + " " + rcond + ")"
        return cond, lranks + rranks, largs + rargs


class UnaryOp(_Node):
    """Represents a transformation applied to one node: ``not``."""
    NOT = object()
    OPS = {NOT: "NOT"}

    def __init__(self, op, node):
        self.op = op
        self.node = node

    def __repr__(self):
        return "UnaryOp({0}, {1})".format(self.OPS[self.op], self.node)

    def sortkey(self):
        return self.node.sortkey()

    def parameterize(self, tables):
        cond, ranks, args = self.node.parameterize(tables)
        ranks = ranks or [cond]
        return "(" + self.OPS[self.op] + " " + cond + ")", ranks, args

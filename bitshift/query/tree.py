__all__ = ["Tree"]

QUERY_TEMPLATE = """SELECT codelet_id, (codelet_rank + %s) AS score
FROM codelets %s
WHERE %s
GROUP BY codelet_id
ORDER BY score DESC
LIMIT %d OFFSET %d""".replace("\n", " ")

class Tree(object):
    """Represents a query tree."""

    def __init__(self, root):
        self._root = root

    def __repr__(self):
        return "Tree({0})".format(self._root)

    @property
    def root(self):
        """The root node of the tree."""
        return self._root

    def sortkey(self):
        """Return a string sort key for the query tree."""
        return self._root.sortkey()

    def serialize(self):
        """Create a string representation of the query for caching.

        :return: Query string representation.
        :rtype: str
        """
        return repr(self)

    def build_query(self, page=1, page_size=10, pretty=False):
        """Convert the query tree into a parameterized SQL SELECT statement.

        :param page: The page number to get results for.
        :type page: int
        :param page_size: The number of results per page.
        :type page_size: int
        :param pretty: Whether to pretty-print the SQL query or not.
        :type pretty: bool

        :return: SQL query data.
        :rtype: 2-tuple of (SQL statement string, query parameter tuple)
        """
        def get_table_join(table):
            tables = {
                "code": ("codelet_code_id", "code_id"),
                "authors": ("author_codelet", "codelet_id"),
                "symbols": ("symbol_code", "code_id")
            }
            tmpl = "INNER JOIN %s ON %s = %s"
            return tmpl % (table, tables[table][0], tables[table][1])

        tables = set()
        cond, ranks, arglist = self._root.parameterize(tables)
        ranks = ranks or [cond]
        score = "((%s) / %d)" % (" + ".join(ranks), len(ranks))
        joins = " ".join(get_table_join(table) for table in tables)
        offset = (page - 1) * page_size

        ## TODO: handle pretty
        query = QUERY_TEMPLATE % (score, joins, cond, page_size, offset)
        return query, tuple(arglist * 2)

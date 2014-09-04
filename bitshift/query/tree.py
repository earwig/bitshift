from . import nodes

__all__ = ["Tree"]

QUERY_TEMPLATE = """SELECT codelet_id, MAX(codelet_rank%s) AS score
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

    def walk(self, node_type=None):
        """Walk through the query tree, returning nodes of a specific type."""
        pending = [self._root]
        while pending:
            node = pending.pop()
            if not node_type or isinstance(node, node_type):
                yield node
            if isinstance(node, nodes.UnaryOp):
                pending.append(node.node)
            elif isinstance(node, nodes.BinaryOp):
                pending.extend([node.left, node.right])

    def build_query(self, page=1, page_size=10):
        """Convert the query tree into a parameterized SQL SELECT statement.

        :param page: The page number to get results for.
        :type page: int
        :param page_size: The number of results per page.
        :type page_size: int

        :return: SQL query data.
        :rtype: 2-tuple of (SQL statement string, query parameter tuple)
        """
        def get_table_joins(tables):
            joins = [
                ("INNER", "code", "codelet_code_id", "code_id"),
                ("LEFT", "authors", "author_codelet", "codelet_id"),
                ("LEFT", "symbols", "symbol_code", "code_id"),
                ("LEFT", "symbol_locations", "sloc_symbol", "symbol_id")
            ]
            tmpl = "%s JOIN %s ON %s = %s"
            for args in joins:
                if args[1] in tables:
                    yield tmpl % args

        tables = set()
        cond, arglist, ranks, need_ranks = self._root.parameterize(tables)
        ranks = ranks or [cond]
        if need_ranks:
            score = " + ((%s) / %d)" % (" + ".join(ranks), len(ranks))
        else:
            score = ""
        joins = " ".join(get_table_joins(tables))
        offset = (page - 1) * page_size

        query = QUERY_TEMPLATE % (score, joins, cond, page_size, offset)
        return query, tuple(arglist * 2 if need_ranks else arglist)

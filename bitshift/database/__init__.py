"""
Subpackage with classes and functions to handle communication with the MySQL
database backend, which manages the search index.
"""

import os

import mmh3
import oursql

from .migration import VERSION, MIGRATIONS
from ..codelet import Codelet
from ..query.nodes import (String, Regex, Text, Language, Author, Date, Symbol,
                           BinaryOp, UnaryOp)

__all__ = ["Database"]

class Database(object):
    """Represents the MySQL database."""

    def __init__(self, migrate=False):
        self._conn = self._connect()
        self._check_version(migrate)

    def _connect(self):
        """Establish a connection to the database."""
        root = os.path.dirname(os.path.abspath(__file__))
        default_file = os.path.join(root, ".my.cnf")
        return oursql.connect(db="bitshift", read_default_file=default_file,
                              autoping=True, autoreconnect=True)

    def _migrate(self, cursor, current):
        """Migrate the database to the latest schema version."""
        for version in xrange(current, VERSION):
            print "Migrating to %d..." % (version + 1)
            for query in MIGRATIONS[version - 1]:
                cursor.execute(query)
            cursor.execute("UPDATE version SET version = ?", (version + 1,))

    def _check_version(self, migrate):
        """Check the database schema version and respond accordingly.

        If the schema is out of date, migrate if *migrate* is True, else raise
        an exception.
        """
        with self._conn.cursor() as cursor:
            cursor.execute("SELECT version FROM version")
            version = cursor.fetchone()[0]
            if version < VERSION:
                if migrate:
                    self._migrate(cursor, version)
                else:
                    err = "Database schema out of date. " \
                          "Run `python -m bitshift.database.migration`."
                    raise RuntimeError(err)

    def _search_with_query(self, cursor, tree, page):
        """Execute an SQL query based on a query tree, and return results.

        The returned data is a 2-tuple of (list of codelet IDs, estimated
        number of total results).
        """
        query, args = tree.build_query(page)
        cursor.execute(query, args)
        ids = [cid for cid, _ in cursor.fetchall()]
        num_results = len(ids)  # TODO: This is not entirely correct
        return ids, num_results

    def _get_authors_for_codelet(self, cursor, codelet_id):
        """Return a list of authors for a given codelet."""
        query = """SELECT author_name, author_url
                   FROM authors
                   WHERE author_codelet = ?"""

        cursor.execute(query, (codelet_id,))
        return cursor.fetchall()

    def _get_symbols_for_code(self, cursor, code_id, tree):
        """Return a list of symbols for a given codelet."""
        query = """SELECT symbol_type, symbol_name, sloc_type, sloc_row,
                          sloc_col, sloc_end_row, sloc_end_col
                   FROM symbols
                   INNER JOIN symbol_locations ON sloc_symbol = symbol_id
                   WHERE symbol_code = ? AND (%s)"""

        conds, args = [], [code_id]
        for node in tree.walk(Symbol):
            node_cond, node_args, _, _ = node.parameterize(set())
            conds.append(node_cond)
            args += node_args
        if not conds:
            return {}
        cond = " OR ".join(conds)

        symbols = {type_: {} for type_ in Symbol.TYPES}
        cursor.execute(query % cond, tuple(args))
        for type_, name, loc_type, row, col, erow, ecol in cursor.fetchall():
            sdict = symbols[Symbol.TYPES[type_]]
            if name not in sdict:
                sdict[name] = ([], [])
            sdict[name][loc_type].append((row, col, erow, ecol))
        for type_, sdict in symbols.items():
            symbols[type_] = [(n, d, u) for n, (d, u) in sdict.iteritems()]
        return symbols

    def _get_codelets_from_ids(self, cursor, ids, tree):
        """Return a list of Codelet objects given a list of codelet IDs."""
        query = """SELECT *
                   FROM codelets
                   INNER JOIN code ON codelet_code_id = code_id
                   INNER JOIN origins ON codelet_origin = origin_id
                   WHERE codelet_id = ?"""

        with self._conn.cursor(oursql.DictCursor) as dict_cursor:
            for codelet_id in ids:
                dict_cursor.execute(query, (codelet_id,))
                row = dict_cursor.fetchall()[0]
                code_id = row["code_id"]
                if row["origin_url_base"]:
                    url = row["origin_url_base"] + row["codelet_url"]
                else:
                    url = row["codelet_url"]
                origin = (row["origin_name"], row["origin_url"])
                authors = self._get_authors_for_codelet(cursor, codelet_id)
                symbols = self._get_symbols_for_code(cursor, code_id, tree)
                yield Codelet(
                    row["codelet_name"], row["code_code"], None,
                    row["code_lang"], authors, url,
                    row["codelet_date_created"], row["codelet_date_modified"],
                    row["codelet_rank"], symbols, origin)

    def _decompose_url(self, cursor, url):
        """Break up a URL into an origin (with a URL base) and a suffix."""
        query = """SELECT origin_id, SUBSTR(?, LENGTH(origin_url_base) + 1)
                   FROM origins
                   WHERE origin_url_base IS NOT NULL
                   AND ? LIKE CONCAT(origin_url_base, "%")"""

        cursor.execute(query, (url, url))
        result = cursor.fetchone()
        return result if result else (1, url)

    def _insert_symbols(self, cursor, code_id, sym_type, symbols):
        """Insert a list of symbols of a given type into the database."""
        query1 = "INSERT INTO symbols VALUES (DEFAULT, ?, ?, ?)"
        query2 = """INSERT INTO symbol_locations VALUES
                    (DEFAULT, ?, ?, ?, ?, ?, ?)"""

        type_id = Symbol.TYPES.index(sym_type)
        for (name, assigns, uses) in symbols:
            cursor.execute(query1, (code_id, type_id, name))
            sym_id = cursor.lastrowid
            params = ([tuple([sym_id, 0] + list(loc)) for loc in assigns] +
                      [tuple([sym_id, 1] + list(loc)) for loc in uses])
            cursor.executemany(query2, params)

    def close(self):
        """Disconnect from the database."""
        self._conn.close()

    def search(self, tree, page=1):
        """
        Search the database for a query and return the *n*\ th page of results.

        :param tree: The query to search for.
        :type tree: :py:class:`~.query.tree.Tree`
        :param page: The result page to display.
        :type page: int

        :return: The total number of results, and the *n*\ th page of results.
        :rtype: 2-tuple of (long, list of :py:class:`.Codelet`\ s)
        """
        query1 = "SELECT 1 FROM cache WHERE cache_id = ?"
        query2 = """SELECT cdata_codelet, cache_count_mnt, cache_count_exp
                    FROM cache
                    INNER JOIN cache_data ON cache_id = cdata_cache
                    WHERE cache_id = ?
                    ORDER BY cdata_index ASC"""
        query3 = "INSERT INTO cache VALUES (?, ?, ?, DEFAULT)"
        query4 = "INSERT INTO cache_data VALUES (?, ?, ?)"

        cache_id = mmh3.hash64(str(page) + ":" + tree.serialize())[0]

        with self._conn.cursor() as cursor:
            cursor.execute(query1, (cache_id,))
            cache_hit = cursor.fetchall()
            if cache_hit:
                cursor.execute(query2, (cache_id,))
                rows = cursor.fetchall()
                num_results = rows[0][1] * (10 ** rows[0][2]) if rows else 0
                ids = [row[0] for row in rows]
            else:
                ids, num_results = self._search_with_query(cursor, tree, page)
                num_exp = max(len(str(num_results)) - 3, 0)
                num_results = int(round(num_results, -num_exp))
                num_mnt = num_results / (10 ** num_exp)
                cursor.execute(query3, (cache_id, num_mnt, num_exp))
                cdata = [(cache_id, c_id, i) for i, c_id in enumerate(ids)]
                cursor.executemany(query4, cdata)
            codelet_gen = self._get_codelets_from_ids(cursor, ids, tree)
            return (num_results, list(codelet_gen))

    def insert(self, codelet):
        """
        Insert a codelet into the database.

        :param codelet: The codelet to insert.
        :type codelet: :py:class:`.Codelet`
        """
        query1 = """INSERT INTO code VALUES (?, ?, ?)
                    ON DUPLICATE KEY UPDATE code_id=code_id"""
        query2 = """INSERT INTO codelets VALUES
                    (DEFAULT, ?, ?, ?, ?, ?, ?, ?)"""
        query3 = "INSERT INTO authors VALUES (DEFAULT, ?, ?, ?)"

        hash_key = str(codelet.language) + ":" + codelet.code.encode("utf8")
        code_id = mmh3.hash64(hash_key)[0]

        with self._conn.cursor() as cursor:
            cursor.execute(query1, (code_id, codelet.language, codelet.code))
            if cursor.rowcount == 1:
                for sym_type, symbols in codelet.symbols.iteritems():
                    self._insert_symbols(cursor, code_id, sym_type, symbols)
            origin, url = self._decompose_url(cursor, codelet.url)
            cursor.execute(query2, (codelet.name, code_id, origin, url,
                                    codelet.rank, codelet.date_created,
                                    codelet.date_modified))
            codelet_id = cursor.lastrowid
            authors = [(codelet_id, a[0], a[1]) for a in codelet.authors]
            cursor.executemany(query3, authors)

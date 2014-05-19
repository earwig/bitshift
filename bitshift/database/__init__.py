"""
Subpackage with classes and functions to handle communication with the MySQL
database backend, which manages the search index.
"""

import os

import mmh3
import oursql

from .migration import VERSION, MIGRATIONS
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
            print "Migrating to %d..." % version + 1
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

    def _search_with_query(self, cursor, query, page):
        """Execute an SQL query based on a query tree, and return results.

        The returned data is a 2-tuple of (list of codelet IDs, estimated
        number of total results).
        """
        base = """SELECT codelet_id
                  FROM codelets %s
                  WHERE %s
                  GROUP BY codelet_id ORDER BY codelet_rank DESC LIMIT 10"""
        conditional, tables, args = query.parameterize()
        joins = " ".join(tables)
        qstring = base % (joins, conditional)
        if page > 1:
            qstring += " OFFSET %d" % ((page - 1) * 10)

        cursor.execute(qstring, args)
        ids = [id for id, in cursor.fetchall()]
        num_results = 0  # TODO: NotImplemented
        return ids, num_results

    def _get_codelets_from_ids(self, cursor, ids):
        """Return a list of Codelet objects given a list of codelet IDs."""
        raise NotImplementedError()  # TODO

    def _decompose_url(self, cursor, url):
        """Break up a URL into an origin (with a URL base) and a suffix."""
        query = """SELECT origin_id, SUBSTR(?, LENGTH(origin_url_base))
                   FROM origins
                   WHERE origin_url_base IS NOT NULL
                   AND ? LIKE CONCAT(origin_url_base, "%")"""

        cursor.execute(query, (url, url))
        result = cursor.fetchone()
        return result if result else (1, url)

    def _insert_symbols(self, cursor, code_id, sym_type, symbols):
        """Insert a list of symbols of a given type into the database."""
        sym_types = ["functions", "classes", "variables"]
        query1 = "INSERT INTO symbols VALUES (DEFAULT, ?, ?, ?)"
        query2 = """INSERT INTO symbol_locations VALUES
                    (DEFAULT, ?, ?, ?, ?, ?, ?)"""

        for (name, decls, uses) in symbols:
            cursor.execute(query1, (code_id, sym_types.index(sym_type), name))
            sym_id = cursor.lastrowid
            params = ([tuple([sym_id, 0] + list(loc)) for loc in decls] +
                      [tuple([sym_id, 1] + list(loc)) for loc in uses])
            cursor.executemany(query2, params)

    def close(self):
        """Disconnect from the database."""
        self._conn.close()

    def search(self, query, page=1):
        """
        Search the database for a query and return the *n*\ th page of results.

        :param query: The query to search for.
        :type query: :py:class:`~.query.tree.Tree`
        :param page: The result page to display.
        :type page: int

        :return: The total number of results, and the *n*\ th page of results.
        :rtype: 2-tuple of (long, list of :py:class:`.Codelet`\ s)
        """
        query1 = """SELECT cdata_codelet, cache_count_mnt, cache_count_exp
                    FROM cache
                    INNER JOIN cache_data ON cache_id = cdata_cache
                    WHERE cache_id = ?"""
        query2 = "INSERT INTO cache VALUES (?, ?, ?, DEFAULT)"
        query3 = "INSERT INTO cache_data VALUES (?, ?)"

        cache_id = mmh3.hash64(str(page) + ":" + query.serialize())[0]

        with self._conn.cursor() as cursor:
            cursor.execute(query1, (cache_id,))
            results = cursor.fetchall()
            if results:  # Cache hit
                num_results = results[0][1] * (10 ** results[0][2])
                ids = [res[0] for res in results]
            else:  # Cache miss
                ids, num_results = self._search_with_query(cursor, query, page)
                num_exp = max(len(str(num_results)) - 3, 0)
                num_results = int(round(num_results, -num_exp))
                num_mnt = num_results / (10 ** num_exp)
                cursor.execute(query2, (cache_id, num_mnt, num_exp))
                cursor.executemany(query3, [(cache_id, c_id) for c_id in ids])
            return (num_results, self._get_codelets_from_ids(cursor, ids))

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

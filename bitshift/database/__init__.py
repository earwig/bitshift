"""
Subpackage with classes and functions to handle communication with the MySQL
database backend, which manages the search index.
"""

import os

import mmh3
import oursql

from .migration import VERSION, MIGRATIONS

__all__ = ["Database"]

class Database(object):
    """Represents the MySQL database."""

    def __init__(self, migrate=False):
        self._connect()
        self._check_version(migrate)

    def _connect(self):
        """Establish a connection to the database."""
        root = os.path.dirname(os.path.abspath(__file__))
        default_file = os.path.join(root, ".my.cnf")
        self._conn = oursql.connect(read_default_file=default_file,
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

        :return: A list of search results.
        :rtype: list of :py:class:`.Codelet`\ s
        """
        # search for cache_hash = mmh3.hash(query.serialize() + str(page))
        #   cache HIT:
        #       update cache_last_used
        #       return codelets
        #   cache MISS:
        #       build complex search query
        #       fetch codelets
        #       cache results
        #       return codelets
        pass

    def insert(self, codelet):
        """
        Insert a codelet into the database.

        :param codelet: The codelet to insert.
        :type codelet: :py:class:`.Codelet`
        """
        query1 = """INSERT INTO code VALUES (?, ?)
                    ON DUPLICATE KEY UPDATE code_id=code_id"""
        query2 = """INSERT INTO codelets VALUES
                    (?, ?, ?, ?, ?, ?, ?, ?)"""
        query3 = "SELECT LAST_INSERT_ID()"
        query4 = "INSERT INTO authors VALUES (?, ?, ?)"
        query5 = "INSERT INTO symbols VALUES (?, ?, ?, ?, ?, ?, ?)"

        code_id = mmh3.hash64(codelet.code.encode("utf8"))[0]
        origin, url = decompose(codelet.url)  ## TODO: create decompose() function

        with self._conn.cursor() as cursor:
            cursor.execute(query1, (code_id, codelet.code))
            cursor.execute(query2, (codelet.name, code_id, codelet.language,
                                    origin, url, codelet.rank,
                                    codelet.date_created,
                                    codelet.date_modified))
            cursor.execute(query3)
            codelet_id = cursor.fetchone()[0]
            authors = [(codelet_id, a.name, a.url) for a in codelet.authors]  ## TODO: check author fields (is it a tuple?)
            cursor.executemany(query4, authors)
            if code_id is new:  ## TODO: check for this properly
                symbols = [(code_id, sym.type, sym.name, sym.row, sym.col, sym.end_row, sym.end_col) for sym in codelet.symbols]  # TODO: check symbol fields (dict?)
                cursor.executemany(query5, symbols)

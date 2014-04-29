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
        query2 = "INSERT INTO codelets VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        query3 = "INSERT INTO authors VALUES", " (?, ?, ?)"
        query4 = "INSERT INTO symbols VALUES", " (?, ?, ?, ?, ?)"

        # LAST_INSERT_ID()

        # codelet_id -- auto_increment used here
        codelet_name
        codelet_code_id
        codelet_lang
        codelet_origin
        codelet_url
        codelet_rank
        codelet_date_created
        codelet_date_modified

        # codelet fields
        codelet.name
        codelet.code
        codelet.filename
        codelet.language
        codelet.authors
        codelet.code_url
        codelet.date_created
        codelet.date_modified

        #######################################################################

        code_id = mmh3.hash64(codelet.code.encode("utf8"))[0]

        with self._conn.cursor() as cursor:
            cursor.execute(query1, (code_id, codelet.code))

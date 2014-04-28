"""
Subpackage with classes and functions to handle communication with the MySQL
database backend, which manages the search index.
"""

import os

import mmh3
import oursql

# from ..languages import ...

__all__ = ["Database"]

class Database(object):
    """Represents the MySQL database."""

    def __init__(self):
        self._connect()

    def _connect(self):
        """Establish a connection to the database."""
        root = os.path.dirname(os.path.abspath(__file__))
        default_file = os.path.join(root, ".my.cnf")
        self._conn = oursql.connect(read_default_file=default_file,
                                    autoping=True, autoreconnect=True)

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
        frag_size = 16384  # 16 kB
        query_slt1 = """SELECT code_id, LEFT(code_code, {0})
                        FROM code WHERE code_hash = ?""".format(frag_size)
        query_ins1 = "INSERT INTO code VALUES (?, ?)"
        query_ins2 = "INSERT INTO codelets VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        query_ins3 = "INSERT INTO authors VALUES", " (?, ?, ?)"
        query_ins4 = "INSERT INTO symbols VALUES", " (?, ?, ?, ?, ?)"

        # LAST_INSERT_ID()

        code_id = None
        code_hash = mmh3.hash64(codelet.code.encode("utf8"))[0]

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

        with self._conn.cursor() as cursor:
            # Retrieve the ID of the source code if it's already in the DB:
            cursor.execute(query_slt1, (code_hash,))
            for c_id, c_code_frag in cursor.fetchall():
                if c_code_frag == codelet.code[:frag_size]:
                    code_id = c_id
                    break

            # If the source code isn't already in the DB, add it:
            if not code_id:
                cursor.execute()

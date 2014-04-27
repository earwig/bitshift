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
        default_file = os.path.join(os.path.dirname(__file__), ".my.cnf")
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
        query = "INSERT INTO codelets VALUES (?, ?, ?, ?, ?, ?, ?, ?)"

        cursor.execute(query, ())

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

        code_hash = mmh3.hash64(codelet.code.encode("utf8"))[0]

"""
Module with classes and functions to handle communication with the MySQL
database backend, which manages the search index.
"""

import mmh3
import oursql

class Database(object):
    """Represents the MySQL database."""

    def __init__(self):
        self._connect()

    def _connect(self):
        """Establish a connection to the database."""
        self._conn = oursql.connect()

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
        # code_hash = mmh3.hash64(codelet.code.encode("utf8"))[0]
        pass

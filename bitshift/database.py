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

    def search(self, query):
        """
        Search the database.

        :param query: The query to search for.
        :type query: :py:class:`~.query.tree.Tree`

        :return: A list of search results.
        :rtype: list of :py:class:`.Codelet`\ s
        """
        pass

    def insert(self, codelet):
        """
        Insert a codelet into the database.

        :param codelet: The codelet to insert.
        :type codelet: :py:class:`.Codelet`
        """
        # code_hash = mmh3.hash64(codelet.code)[0]
        pass

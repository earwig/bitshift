__all__ = ["Codelet"]

class Codelet(object):
    """
    A source-code object with code metadata and composition analysis.

    :ivar code: (str) A containing the raw source code.
    :ivar filename: (str, or None) The filename of the snippet.
    :ivar language: (str, or None) The inferred language of `code`.
    :ivar authors: (array of str tuple) An array of tuples containing an
        author's name and profile URL (on the service the code was pulled from).
    :ivar code_url: (str) The url of the (page containing the) source code.
    :ivar date_created: (str, or None) The date the code was published.
    :ivar date_modified: (str, or None) The date the code was last modified.
    """

    def __init__(self, name, code, filename, language, authors, code_url,
                 date_created, date_modified):
        """
        Create a Codelet instance.

        :param code: The raw source code.
        :param filename: The filename of the code, if any.
        :param language: The inferred language.
        :param authors: An array of tuples containing an author's name and
            profile URL (on the service the code was pulled from).
        :param code_url: The url of the (page containing the) source code.
        :param date_created: The date the code was published.
        :param date_modified: The date the code was last modified.

        :type code: str
        :type filename: str, or None
        :type authors: array of str tuples, or None
        :type language: str, or None
        :type code_url: str
        :type author_urls: str array, or none
        :type date_created: str, or None
        :type date_modified: str, or None
        """

        self.code = code
        self.filename = filename
        self.language = language
        self.authors = authors
        self.code_url = code_url
        self.date_created = date_created
        self.date_modified = date_modified

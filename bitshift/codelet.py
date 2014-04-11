__all__ = ["Codelet"]

class Codelet(object):
    """
    A source-code object with code metadata and composition analysis.

    :ivar code: (str) A containing the raw source code.
    :ivar filename: (str, or None) The filename of the snippet.
    :ivar language: (str, or None) The inferred language of `code`.
    :ivar author: (str, or None) The name of the code's author.
    :ivar url: (str) The url of the (page containing the) source code.
    :ivar date_created: (str, or None) The date the code was published.
    :ivar date_modified: (str, or None) The date the code was last modified.
    """

    def __init__(self, code, filename, author, language, code_url, author_url,
                 date_created, date_modified):
        """
        Create a Codelet instance.

        :param code: The raw source code.
        :param filename: The filename of the code, if any.
        :param author: The author of the code.
        :param language: The inferred language.
        :param code_url: The url of the (page containing the) source code.
        :param date_created: The date the code was published.
        :param date_modified: The date the code was last modified.

        :type code: str
        :type filename: str, or None
        :type language: str, or None
        :type author: str, or None
        :type url: str
        :type date_created: str, or None
        :type date_modified: str, or None
        """

        self.code = code
        self.filename = filename
        self.author = author
        self.language = language
        self.code_url = code_url
        self.author_url = author_url
        self.date_created = date_created
        self.date_modified = date_modified

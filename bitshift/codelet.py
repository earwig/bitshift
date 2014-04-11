__all__ = ["Codelet"]

class Codelet(object):
    """
    A source-code object with code metadata and composition analysis.

    :ivar code: (string) A containing the raw source code.
    :ivar language: (string) The inferred language of `code`.
    :ivar author: (string) The
    :ivar url: The url of the (page containing the) source code.
    :ivar date_created: The date the code was published.
    :ivar date_modified: The date the code was last modified.
    """

    def __init__(self, code, author, language, code_url, author_url,
            date_created, date_modified):
        """
        Create a Codelet instance.

        :param code: The raw source code.
        :param author: The author of the code.
        :param language: The inferred language.
        :param code_url: The url of the (page containing the) source code.
        :param author_url: The url of the code author's public profile on the
            framework said code was retrieved from.
        :param date_created: The date the code was published.
        :param date_modified: The date the code was last modified.

        :type code: string
        :type language: string
        :type author: string
        :type url: string
        :type date_created: string
        :type date_modified: string
        """

        self.code = code
        self.author = author
        self.language = language
        self.code_url = code_url
        self.author_url = author_url
        self.date_created = date_created
        self.date_modified = date_modified

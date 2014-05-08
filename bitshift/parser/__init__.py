import json, pygments.lexers as pgl, sys, socket, struct
from ..languages import LANGS
from .python import parse_py

_all__ = ["parse"]

class UnsupportedFileError(Exception):
    pass

def _lang(codelet):
    """
    Private function to identify the language of a codelet.

    :param codelet: The codelet object to identified.

    :type code: Codelet

    .. todo::
        Modify function to incorporate tags from stackoverflow.
    """

    if codelet.filename is not None:
        try:
            return pgl.guess_lexer_for_filename(codelet.filename, '').name
        except:
            raise UnsupportedFileError('Could not find a lexer for the codelet\'s filename')

    return LANGS.index(pgl.guess_lexer(codelet.code))

def _recv_data(server_socket):
    """
    Private function to read string response from a server.  It reads a certain
        amount of data based on the size it is sent from the server.

    :param server_socket: The server that the client is connected to, and will,
        read from.

    :type code: socket.ServerSocket
    """

    recv_size = 8192
    total_data = []; size_data = cur_data = ''
    total_size = 0; size = sys.maxint

    while total_size < size:
        cur_data = server_socket.recv(recv_size)

        if not total_data:
            if len(size_data) > 4:
                size_data += cur_data
                size = struct.unpack('>i', size_data[:4])[0]
                recv_size = size
                if recv_size > sys.maxint: recv_size = sys.maxint
                total_data.append(size_data[4:])
            else:
                size_data += cur_data

        else:
            total_data.append(cur_data)

        total_size = sum([len(s) for s in total_data])

    server_socket.close()
    return ''.join(total_data);


def parse(codelet):
    """
    Dispatches the codelet to the correct parser based on its language.
        It is the job of the respective parsers to accumulate data about the
        code and to convert it into a string representing a python dict.
        The codelet is then given dict as its 'symbols' field.

    :param codelet: The codelet object to parsed.

    :type code: Codelet
    """

    lang = _lang(codelet); source = codelet.code
    codelet.language = lang
    server_socket_number = 5000 + lang

    if lang == LANGS.index('Python'):
        parse_py(codelet)

    else:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect(("localhost", server_socket_number))
        server_socket.send("%d\n%s" % (len(source), source));

        symbols = json.loads(_recv_data(server_socket))
        codelet.symbols = symbols


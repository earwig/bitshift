import json
import sys
import socket
import struct
import subprocess

from os import path
from pygments import lexers as pgl, util

from ..languages import LANGS, LANGS_ALL
from .python import parse_py

__all__ = ["parse", "UnsupportedFileError", "start_parse_servers"]

PARSER_COMMANDS = [
        ('Java', ['mvn', '-f',
            path.join(path.dirname(__file__), "../../parsers/java/pom.xml"),
            'exec:java', '-Dexec.args=%d']),
        ('Ruby', ['rake', '-f',
            path.join(path.dirname(__file__), "../../parsers/ruby/Rakefile"),
            'start_server[%d]'])
]

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

    try:
        if codelet.filename:
            lex = pgl.guess_lexer_for_filename(codelet.filename, codelet.code)
        else:
            lex = pgl.guess_lexer(codelet.code)
        return LANGS_ALL[lex.name]
    except (util.ClassNotFound, KeyError):
        raise UnsupportedFileError(codelet.filename)

def _recv_data(server_socket):
    """
    Private function to read string response from a server.  It reads a certain
        amount of data based on the size it is sent from the server.

    :param server_socket: The server that the client is connected to, and will,
        read from.

    :type code: socket.ServerSocket
    """

    recv_size = 8192
    total_data = []
    size_data = cur_data = ''
    total_size, size = 0, sys.maxint

    while total_size < size:
        cur_data = server_socket.recv(recv_size)

        if not total_data:
            if len(size_data) > 4:
                size_data += cur_data
                size = struct.unpack('>i', size_data[:4])[0]
                recv_size = size
                if recv_size > sys.maxint:
                    recv_size = sys.maxint
                total_data.append(size_data[4:])
            else:
                size_data += cur_data

        else:
            total_data.append(cur_data)

        total_size = sum([len(s) for s in total_data])

    server_socket.close()
    return ''.join(total_data)

def start_parse_servers():
    """
    Starts all the parse servers for languages besides python.

    :rtype: list
    """

    procs = []

    for (lang, cmd) in PARSER_COMMANDS:
        cmd[-1] = cmd[-1] % (5001 + LANGS.index(lang))
        procs.append(subprocess.Popen(cmd))

    return procs

def parse_via_server(codelet):
    port = 5001 + codelet.language
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect(("localhost", port))
    server_socket.send("%d\n%s" % (len(codelet.code), codelet.code))

    symbols = json.loads(_recv_data(server_socket))
    return symbols

PARSERS = {
    "Python": parse_py,
    "Java":   parse_via_server,
    "Ruby":   parse_via_server,
}

def parse(codelet):
    """
    Dispatches the codelet to the correct parser based on its language.
        It is the job of the respective parsers to accumulate data about the
        code and to convert it into a string representing a python dict.
        The codelet is then given dict as its 'symbols' field.

    :param codelet: The codelet object to parsed.

    :type code: Codelet
    """
    lang = _lang(codelet)
    lang_string = LANGS[lang]
    codelet.language = lang

    def loc_helper(l):
        for i in l:
            if i == -1:
                yield None
            else:
                yield i

    if lang_string in PARSERS:
        symbols = PARSERS[lang_string](codelet)
        symbols = {
            key: [(name,
                   [tuple(loc_helper(loc)) for loc in syms[name]["assignments"]],
                   [tuple(loc_helper(loc)) for loc in syms[name]["uses"]])
                  for name in syms]
            for key, syms in symbols.iteritems()}
        codelet.symbols = symbols

import os, ast
import pygments.lexers as pgl
from ..languages import LANGS
from .python import parse_py

_all__ = ["parse"]

def _lang(codelet):
    """
    Private function to identify the language of a codelet.

    :param codelet: The codelet object to identified.

    :type code: Codelet

    .. todo::
        Modify function to incorporate tags from stackoverflow.
    """

    if codelet.filename is not None:
        return pgl.guess_lexer_for_filename(codelet.filename).name

    return LANGS.index(pgl.guess_lexer(codelet.code))

def parse(codelet, pid):
    """
    Sends codelet code to the Java parsing process via a named pipe. Reads the
        resulting symbols from the pipe and updates the codelet.

    :param codelet: The codelet object to parsed.
    :param pid: The id of the current python process.

    :type code: Codelet
    :param pid: str.

    .. todo::
        Identify languages using pygments and change the write file based on
        that.
    """

    codelet.language = _lang(codelet)

    if codelet.language == LANGS.index("Python"):
        parse_py(codelet)

    else:
        write_f = "../../tmp/%d_parser.proc" % codelet.language

        with open(write_f, 'a') as wf:
            wf.write('pid:' + str(pid) + '\n')
            wf.write('body:\n' + codelet.code)

        read_f = '../../tmp/%s_py.data' % str(pid)
        data = ''

        while data == '':
            with open(read_f) as rf:
                data = rf.read()

        os.remove(read_f)
        codelet.symbols = ast.literal_eval(data.split(',')[1])


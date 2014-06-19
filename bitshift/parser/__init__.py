import json
import subprocess

from os import path
from pygments import lexers as pgl, util

from ..languages import LANGS, LANGS_ALL
from .python import parse_py

__all__ = ["parse", "UnsupportedFileError", "start_parse_servers"]

# TODO: Change these
PARSER_COMMANDS = {
        'Java': ['java', '-cp',
            path.join(path.dirname(__file__), "../../parsers/java/parsing.jar"),
            'com.bitshift.parsing.Parse'],
        'Ruby': ['rake', '-f',
            path.join(path.dirname(__file__), "../../parsers/ruby/Rakefile"),
            'parse']
}

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

def parse_via_proc(codelet):
    proc = subprocess.Popen(PARSER_COMMANDS[LANGS[codelet.language]],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    data = proc.communicate(codelet.code)[0]
    symbols = json.loads(data)
    return symbols

PARSERS = {
    "Python": parse_py,
    "Java":   parse_via_proc,
    "Ruby":   parse_via_proc,
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

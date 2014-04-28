import pygments.lexers as pgl
from ..languages import LANGS
from .python import parse_py
from .c import parse_c
from .java import parse_java
from .ruby import parse_ruby

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
    Dispatches the codelet to the correct parser based on its language.

    :param codelet: The codelet object to parsed.
    :param pid: The id of the current python process.

    :type code: Codelet
    :param pid: str.
    """

    lang = _lang(codelet)

    if lang == LANGS.index("Python"):
        parse_py(codelet)

    elif lang == LANGS.index("C"):
        parse_c(codelet)

    elif lang == LANGS.index("Java"):
        parse_java(codelet)

    elif lang == LANGS.index("Ruby"):
        parse_ruby(codelet)


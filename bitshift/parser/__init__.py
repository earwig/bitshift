from .python import parse_py
from .c import parse_c
from ..languages import LANGS
import pygments.lexers as pgl

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

def parse(codelet):
    """
    Dispatch codelet to correct parser by language of code.

    :param codelet: The codelet object to parsed.

    :type code: Codelet
    """

    lang = _lang(codelet)

    if lang == LANGS.index("Python"):
        parse_py(codelet)
    elif lang == LANGS.index("C"):
        parse_c(codelet)


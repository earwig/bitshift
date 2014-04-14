from .python import parse_py
from .c import parse_c
from .java import parse_java
from bitshift.config import LANG_PYTHON, LANG_C, LANG_JAVA, PYG_IDS
import pygments.lexers as pgl

_all__ = ["parse"]

# TODO: modify to incorporate tags from stackoverflow
def _lang(codelet):
    """
    Private function to identify the language of a codelet.

    :param codelet: The codelet object to identified.

    :type code: Codelet
    """
    if codelet.filename is not None:
        return pgl.guess_lexer_for_filename(codelet.filename).name

    return PYG_IDS[pgl.guess_lexer(codelet.code)]

def parser(codelet):
    """
    Dispatch codelet to correct parser by language of code.

    :param codelet: The codelet object to parsed.

    :type code: Codelet
    """
    lang = _lang(codelet)

    if lang == LANG_PYTHON:
        parse_py(codelet)
    elif lang == LANG_C:
        parse_c(codelet)
    elif lang == LANG_JAVA:
        parse_java(codelet)


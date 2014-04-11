from .python import parse_py
from .c import parse_c
from .java import parse_java
import pygments.lexers as pgl

_all__ = ["parse"]

# TODO: modify to incorporate tags from stackoverflow
def _lang(codelet):
    if codelet.filename is not None:
        return pgl.guess_lexer_for_filename(codelet.filename).name

    return pgl.guess_lexer(codelet.code)

# dispatches the codelet to the correct parser
def parser(codelet):
    lang = _lang(codelet)

    if lang == "Python":
        parse_py(codelet)
    elif lang == "C":
        parse_c(codelet)
    elif lang == "Java":
        parse_java(codelet)


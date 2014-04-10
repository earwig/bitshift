__all__ = ["Codelet"]

class Codelet(object):
    ## object to store the following (it doesn't need to do anything with it):
    ## author name, URL, date created/modified, language, source code itself
    ## for VCS: project name, file in project
    ## also: list of functions, etc (associations data)

    ## DICTIONARY MAPPING STRINGS REPRESENTING ASSOCIATION TYPE WITH DICTIONARIES
    ## MAPPING ASSOCIATION NAMES WITH TUPLES REPRESENTING THEIR PLACE IN THE FILE
    ## STORED AS TWO INTEGERS REPRESENTING THE ROW AND THE COLUMN

    ## {"functions": {"foo": (12, 13), "bar": (53, 3)}}

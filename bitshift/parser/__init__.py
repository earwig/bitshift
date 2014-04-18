import os

_all__ = ["parse"]

def parse(codelet):
    """
    Sends codelet code to the Java parsing process via a named pipe. Reads the
        resulting symbols from the pipe and updates the codelet.

    :param codelet: The codelet object to parsed.

    :type code: Codelet

    .. todo::
        Create a named pipe for python process to communicate with Java
        process.

        Send the process id and codelet code through the named pipe.

        Read the result from the named pipe and turn it into a dict.
    """
    pass


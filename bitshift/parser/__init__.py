import os, ast

_all__ = ["parse"]

WRITE_F = "../../tmp/parser.proc"

def parse(codelet, pid):
    """
    Sends codelet code to the Java parsing process via a named pipe. Reads the
        resulting symbols from the pipe and updates the codelet.

    :param codelet: The codelet object to parsed.
    :param pid: The id of the current python process.

    :type code: Codelet
    :param pid: str.

    .. todo::
        Create a named pipe for python process to communicate with Java
        process.

        Send the process id and codelet code through the named pipe.

        Read the result from the named pipe and turn it into a dict.
    """

    with open(WRITE_F, 'a') as wf:
        wf.write('pid:' + str(pid) + '\n')
        wf.write('body:\n' + codelet.code)

    read_f = '../../tmp/%s_py.data' % str(pid)
    data = ''

    while data == '':
        with open(read_f) as rf:
            data = rf.read()

    os.remove(read_f)

    results = data.split('\n')
    codelet.language = results[0].split(',')[1]
    codelet.symbols = ast.literal_eval(results[1].split(',')[1])


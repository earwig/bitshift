import ast

def _serialize(tree):
    """
    Private function to serialize an abstract syntax tree so it is indexable by the database.

    :param tree: The syntax tree to be serialized.

    :type tree: list or ast.AST
    """

    def _start_n_end(big_node):
        """
        Helper function to get the start and end lines of a code node.

        :param big_node: The node.

        :type big_node: ast.FunctionDef, ast.ClassDef, ast.Module
        """

        start_line = big_node.lineno

        temp_node = big_node
        while 'body' in temp_node.__dict__:
            temp_node = temp_node.body[-1]

        end_line = temp_node.lineno
        return (start_line, end_line)

    def _helper(cur_node, accum):
        """
        Helper function for _serialize which recursively updates the 'vars', 'functions', and 'classes' in the parsed version of the tree.

        :param cur_node: The node in the syntax tree currently being parsed.
        :param accum: Dicitonary holding parsed version of the tree.

        :type cur_node: list or ast.AST
        :type accum: dict
        """

        if isinstance(cur_node, list):
            for node in cur_node:
                _helper(node, accum)

        elif isinstance(cur_node, ast.Assign):
            # return name
            # return col and line offset
            # in the future add value and type metadata
            for t in cur_node.targets:
                if isinstance(t, ast.Tuple):
                    for n in t.elts:
                        line, col = n.lineno, n.col_offset
                        accum['vars'][n.id] = {'ln': line, 'col': col}
                else:
                    line, col = t.lineno, t.col_offset
                    accum['vars'][t.id] = {'ln': line, 'col': col}


        elif isinstance(cur_node, ast.FunctionDef):
            # return name
            # return start and end of the function
            # in the future add arguments and decorators metadata
            start_line, end_line = _start_n_end(cur_node)
            accum['functions'][cur_node.name] = {'start_ln': start_line , 'end_ln': end_line}

        elif isinstance(cur_node, ast.ClassDef):
            # return name
            # return start and end of the class
            # in the future add arguments, inherits, and decorators metadata
            start_line, end_line = _start_n_end(cur_node)
            accum['classes'][cur_node.name] = {'start_ln': start_line , 'end_ln': end_line}

        if isinstance(cur_node, ast.AST):
            for k in cur_node.__dict__.keys():
                node = cur_node.__dict__[k]
                _helper(node, accum)

    accum = {'vars': {}, 'functions': {}, 'classes': {}}
    _helper(tree, accum)
    return accum

def parse_py(codelet):
    """
    Adds 'symbols' field to the codelet after parsing the code.

    :param codelet: The codelet object to parsed.

    :type code: Codelet
    """
    tree = ast.parse(codelet.code)
    symbols = _serialize(tree)
    codelet.symbols = symbols
    print symbols

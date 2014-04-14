import ast

class PyTreeCutter(ast.NodeVisitor):
    """
    Local node visitor for python abstract syntax trees.

    :ivar accum: (dict) Relevant data accumulated from an abstract syntax tree.
    """

    def __init__(self):
        """
        Create a PyTreeCutter instance.
        """

        self.accum = {'vars': {}, 'functions': {}, 'classes': {}}

    def start_n_end(self, big_node):
        """
        Helper function to get the start and end lines of an AST node.

        :param big_node: The node.

        :type big_node: ast.FunctionDef or ast.ClassDef or ast.Module
        """

        start_line = big_node.lineno

        temp_node = big_node
        while 'body' in temp_node.__dict__:
            temp_node = temp_node.body[-1]

        end_line = temp_node.lineno
        return (start_line, end_line)

    def visit_Assign(self, node):
        """
        Visits Assign nodes in a tree.  Adds relevant data about them to accum.

        :param node: The current node.

        :type node: ast.Assign

        .. todo::
            Add value and type metadata to accum.
        """

        for t in node.targets:
            if isinstance(t, ast.Tuple):
                for n in t.elts:
                    line, col = n.lineno, n.col_offset
                    self.accum['vars'][n.id] = {'ln': line, 'col': col}
            else:
                line, col = t.lineno, t.col_offset
                self.accum['vars'][t.id] = {'ln': line, 'col': col}

        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        """
        Visits FunctionDef nodes in a tree.  Adds relevant data about them to accum.

        :param node: The current node.

        :type node: ast.FunctionDef

        .. todo::
            Add arguments and decorators metadata to accum.
        """

        start_line, end_line = self.start_n_end(node)
        self.accum['functions'][node.name] = {'start_ln': start_line,
            'end_ln': end_line}

        self.generic_visit(node)

    def visit_ClassDef(self, node):
        """
        Visits ClassDef nodes in a tree.  Adds relevant data about them to accum.

        :param node: The current node.

        :type node: ast.ClassDef

        .. todo::
            Add arguments, inherits, and decorators metadata to accum.
        """
        start_line, end_line = self.start_n_end(node)
        self.accum['functions'][node.name] = {'start_ln': start_line,
            'end_ln': end_line}

        self.generic_visit(node)

def parse_py(codelet):
    """
    Adds 'symbols' field to the codelet after parsing the code.

    :param codelet: The codelet object to parsed.

    :type code: Codelet
    """

    tree = ast.parse(codelet.code)
    cutter = PyTreeCutter()
    cutter.visit(tree)
    codelet.symbols = cutter.accum

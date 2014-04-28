import ast

class _TreeCutter(ast.NodeVisitor):
    """
    Local node visitor for python abstract syntax trees.

    :ivar accum: (dict) Information on variables, functions, and classes
        accumulated from an abstract syntax tree.

    :ivar cache: (dict or None) Information stored about parent nodes. Added
        to accum when node reaches the lowest possible level.

    .. todo::
        Add visit funciton for ast.Name to record all uses of a variable.

        Use self.cache to store extra information about nodes.
    """

    def __init__(self):
        """
        Create a _TreeCutter instance.
        """

        self.accum = {'vars': {}, 'functions': {}, 'classes': {}}
        self.cache = None

    def start_n_end(self, node):
        """
        Helper function to get the start and end lines of an AST node.

        :param node: The node.

        :type node: ast.FunctionDef or ast.ClassDef or ast.Module
        """

        start_line, start_col = node.lineno, node.col_offset

        temp_node = node
        while 'body' in temp_node.__dict__:
            temp_node = temp_node.body[-1]

        end_line, end_col = temp_node.lineno, temp_node.col_offset
        return (start_line, start_col, end_line, end_col)

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

                    if not self.accum['vars'].has_key(node.name):
                        self.accum['vars'][node.name] = {'declaration': {}, 'uses': []}

                    pos = {'coord': {}}
                    pos['coord']['start_line'] = line
                    pos['coord']['start_col'] = col
                    pos['coord']['end_line'] = line
                    pos['coord']['end_col'] = col
                    self.accum['vars'][n.id]['declaration'] = pos

            else:
                line, col = t.lineno, t.col_offset

                pos = {'coord': {}}
                pos['coord']['start_line'] = line
                pos['coord']['start_col'] = col
                pos['coord']['end_line'] = line
                pos['coord']['end_col'] = col
                self.accum['vars'][t.id]['declaration'] = pos

        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        """
        Visits FunctionDef nodes in a tree.  Adds relevant data about them to accum.

        :param node: The current node.

        :type node: ast.FunctionDef

        .. todo::
            Add arguments and decorators metadata to accum.
        """

        start_line, start_col, end_line, end_col = self.start_n_end(node)

        if not self.accum['functions'].has_key(node.name):
            self.accum['functions'][node.name] = {'declaration': {}, 'calls': []}

        pos = {'coord': {}}
        pos['coord']['start_ln']= start_line
        pos['coord']['start_col'] = start_col
        pos['coord']['end_ln'] = end_line
        pos['coord']['end_col'] = end_col
        self.accum['functions'][node.name]['declaration'] = pos

        self.generic_visit(node)

    def visit_Call(self, node):
        """
        Visits Function Call nodes in a tree.  Adds relevant data about them
            in the functions section for accum.

        :param node: The current node.

        :type node: ast.Call

        .. todo::
            Add arguments and decorators metadata to accum.
        """

        line, col = node.line_no, node.col_offset

        if not self.accum['functions'].has_key(node.name):
            self.accum['functions'][node.name] = {'declaration': {}, 'calls': []}

        pos = {'coord': {}}
        pos['coord']['start_line'] = line
        pos['coord']['start_col'] = col
        pos['coord']['end_line'] = line
        pos['coord']['end_col'] = col
        self.accum['functions'][node.name]['calls'].append(pos)

        self.generic_visit(node)


    def visit_ClassDef(self, node):
        """
        Visits ClassDef nodes in a tree.  Adds relevant data about them to accum.

        :param node: The current node.

        :type node: ast.ClassDef

        .. todo::
            Add arguments, inherits, and decorators metadata to accum.
        """

        start_line, start_col, end_line, end_col = self.start_n_end(node)

        pos = {'coord': {}}
        pos['coord']['start_ln']= start_line
        pos['coord']['start_col'] = start_col
        pos['coord']['end_ln'] = end_line
        pos['coord']['end_col'] = end_col
        self.accum['classes'][node.name] = pos

        self.generic_visit(node)

    def visit_Name(self, node):
        pass

def parse_py(codelet):
    """
    Adds 'symbols' field to the codelet after parsing the python code.

    :param codelet: The codelet object to parsed.

    :type code: Codelet
    """

    tree = ast.parse(codelet.code)
    cutter = _TreeCutter()
    cutter.visit(tree)
    codelet.symbols = cutter.accum

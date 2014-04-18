from pycparser import c_parser, c_ast

class _TreeCutter(c_ast.NodeVisitor):
    """
    Local node visitor for c abstract syntax trees.

    :ivar accum: (dict) Information on variables, functions, and structs
        accumulated from an abstract syntax tree.

    :ivar cache: (dict or None) Information stored about parent nodes. Added
        to accum when node reaches the lowest possible level.

    .. todo::
        Add visit function for c_ast.ID to record all uses of a variable.

        Use self.cache to store extra information about variables.
    """

    def __init__(self):
        """
        Create a _TreeCutter instance.
        """

        self.accum = {'vars': {}, 'functions': {}, 'structs': {}}
        self.cache = None

    def start_n_end(self, node):
        pass

    def visit_FuncDecl(self, node):
        """
        Visits FuncDecl nodes in a tree.  Adds relevant data about them to accum
            after visiting all of its children as well.

        :param node: The current node.

        :type node: c_ast.FuncDecl

        .. todo::
            Add other relevant information about functions like parameters and
                return type.
        """

        self.cache['group'] = 'functions'
        self.cache['meta']['end_ln'] = node.coord.line
        self.cache['meta']['end_col'] = node.coord.column

        self.generic_visit(node)

    def visit_Struct(self, node):
        """
        Visits Struct nodes in a tree.  Adds relevant data about them to accum
            after visiting all of its children as well.

        :param node: The current node.

        :type node: c_ast.Struct

        .. todo::
            Find other relevant information to add about structs.
        """

        self.cache['group'] = 'structs'
        self.cache['meta']['end_ln'] = node.coord.line
        self.cache['meta']['end_col'] = node.coord.column

        self.generic_visit(node)

    def visit_Decl(self, node):
        """
        Visits Decl nodes in a tree.  Adds relevant data about them to accum
            after visiting all of its children as well.

        :param node: The current node.

        :type node: c_ast.Decl
        """

        self.cache = {'group': 'vars', 'meta': {}}

        self.cache['meta']['start_ln'] = node.coord.line
        self.cache['meta']['start_col'] = node.coord.column
        self.cache['meta']['end_ln'] = node.coord.line
        self.cache['meta']['end_col'] = node.coord.column

        self.generic_visit(node)

        self.accum[self.cache['group']][node.name] = self.cache['meta']
        self.cache = None

def parse_c(codelet):
    """
    Adds 'symbols' field to the codelet after parsing the c code.

    :param codelet: The codelet object to parsed.

    :type code: Codelet

    .. todo::
        Preprocess c code so that no ParseErrors are thrown.
    """

    tree = c_parser.CParser().parse(codelet.code)
    cutter = _TreeCutter()
    cutter.visit(tree)
    codelet.symbols = cutter.accum

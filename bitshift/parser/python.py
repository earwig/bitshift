import ast
import re

encoding_re = re.compile(r"^\s*#.*coding[:=]\s*([-\w.]+)", re.UNICODE)

class _CachedWalker(ast.NodeVisitor):
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
        self.cache = []

    def block_position(self, node):
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

        line, col = node.lineno, node.col_offset
        pos = (line, col, -1, -1)

        self.cache.append({'nodes': []})
        self.generic_visit(node)
        last = self.cache.pop()

        for name in last['nodes']:
            if not self.accum['vars'].has_key(name):
                self.accum['vars'][name] = {'assignments': [], 'uses': []}

            self.accum['vars'][name]['assignments'].append(pos)


    def visit_FunctionDef(self, node):
        """
        Visits FunctionDef nodes in a tree.  Adds relevant data about them to accum.

        :param node: The current node.

        :type node: ast.FunctionDef

        .. todo::
            Add arguments and decorators metadata to accum.
        """

        start_line, start_col, end_line, end_col = self.block_position(node)

        if not self.accum['functions'].has_key(node.name):
            self.accum['functions'][node.name] = {'assignments': [], 'uses': []}

        pos = (start_line, start_col, end_line, end_col)
        self.accum['functions'][node.name]['assignments'].append(pos)

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

        line, col = node.lineno, node.col_offset
        pos = (line, col, -1, -1)

        if isinstance(node.func, ast.Name):
            name = node.func.id
        elif isinstance(node.func, ast.Attr):
            name = node.func.attr
        else:  # Dynamically selected functions, etc:
            return

        if not self.accum['functions'].has_key(name):
            self.accum['functions'][name] = {'assignments': [], 'uses': []}

        self.accum['functions'][name]['uses'].append(pos)

    def visit_ClassDef(self, node):
        """
        Visits ClassDef nodes in a tree.  Adds relevant data about them to accum.

        :param node: The current node.

        :type node: ast.ClassDef

        .. todo::
            Add arguments, inherits, and decorators metadata to accum.
        """

        start_line, start_col, end_line, end_col = self.block_position(node)

        pos = (start_line, start_col, end_line, end_col)
        if node.name not in self.accum['classes']:
            self.accum['classes'][node.name] = {'assignments': [], 'uses': []}
        self.accum['classes'][node.name]['assignments'].append(pos)

        self.generic_visit(node)

    def visit_Name(self, node):
        if self.cache:
            last = self.cache[-1]
            last['nodes'].append(node.id)

    def visit_Attribute(self, node):
        if self.cache:
            last = self.cache[-1]
            last['nodes'].append(node.attr)

def parse_py(codelet):
    """
    Adds 'symbols' field to the codelet after parsing the python code.

    :param codelet: The codelet object to parsed.

    :type code: Codelet
    """

    def strip_encoding(lines):
        """Strips the encoding line from a file, which breaks the parser."""
        it = iter(lines)
        try:
            first = next(it)
            if not encoding_re.match(first):
                yield first
            second = next(it)
            if not encoding_re.match(second):
                yield second
        except StopIteration:
            return
        for line in it:
            yield line

    try:
        tree = ast.parse("\n".join(strip_encoding(codelet.code.splitlines())))
    except SyntaxError:
        ## TODO: add some logging here?
        return
    cutter = _CachedWalker()
    cutter.visit(tree)
    return cutter.accum

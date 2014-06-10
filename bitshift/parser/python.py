import ast
import re

encoding_re = re.compile(r"^\s*#.*coding[:=]\s*([-\w.]+)", re.UNICODE)

class _TreeWalker(ast.NodeVisitor):
    """
    Local node visitor for python abstract syntax trees.

    :ivar symbols: (dict) Information on variables, functions, and classes
        symbolsulated from an abstract syntax tree.

    :ivar cache: (dict or None) Information stored about parent nodes. Added
        to symbols when node reaches the lowest possible level.

    .. todo::
        Add visit funciton for ast.Name to record all uses of a variable.

        Use self.cache to store extra information about nodes.
    """

    def __init__(self):
        """
        Create a _TreeCutter instance.
        """

        self.symbols = {'vars': {}, 'functions': {}, 'classes': {}}
        self.cache = []

    def clear_cache(self):
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

        if start_line == end_line:
            return [start_line, start_col, end_line, -1]

        return [start_line, start_col, end_line, end_col]

    def visit_Assign(self, node):
        """
        Visits Assign nodes in a tree.  Adds relevant data about them to symbols.

        :param node: The current node.

        :type node: ast.Assign

        .. todo::
            Add value and type metadata to symbols.
        """

        pos = self.block_position(node)

        for t in node.targets:
            self.visit(t)

        for name in self.cache:
            if not self.symbols['vars'].has_key(name):
                self.symbols['vars'][name] = {'assignments': [], 'uses': []}

            self.symbols['vars'][name]['assignments'].append(pos)

        self.clear_cache()
        self.visit(node.value)

        for name in self.cache:
            if not self.symbols['vars'].has_key(name):
                self.symbols['vars'][name] = {'assignments': [], 'uses': []}

            self.symbols['vars'][name]['uses'].append(pos)

        self.clear_cache()

    def visit_FunctionDef(self, node):
        """
        Visits FunctionDef nodes in a tree.  Adds relevant data about them to symbols.

        :param node: The current node.

        :type node: ast.FunctionDef

        .. todo::
            Add arguments and decorators metadata to symbols.
        """

        pos = self.block_position(node)

        if not self.symbols['functions'].has_key(node.name):
            self.symbols['functions'][node.name] = {'assignments': [], 'uses': []}

        self.symbols['functions'][node.name]['assignments'].append(pos)

        self.generic_visit(node)

    def visit_Call(self, node):
        """
        Visits Function Call nodes in a tree.  Adds relevant data about them
            in the functions section for symbols.

        :param node: The current node.

        :type node: ast.Call

        .. todo::
            Add arguments and decorators metadata to symbols.
        """

        pos = self.block_position(node)

        self.visit(node.func)
        name = self.cache.pop()

        if not self.symbols['functions'].has_key(name):
            self.symbols['functions'][name] = {'assignments': [], 'uses': []}

        self.symbols['functions'][name]['uses'].append(pos)

        for name in self.cache:
            if not self.symbols['vars'].has_key(name):
                self.symbols['vars'][name] = {'assignments': [], 'uses': []}

            self.symbols['vars'][name]['uses'].append(pos)

        self.clear_cache()

        for a in node.args:
            self.visit(a)

        for name in self.cache:
            if not self.symbols['vars'].has_key(name):
                self.symbols['vars'][name] = {'assignments': [], 'uses': []}

            self.symbols['vars'][name]['uses'].append(pos)

        self.clear_cache()

    def visit_ClassDef(self, node):
        """
        Visits ClassDef nodes in a tree.  Adds relevant data about them to symbols.

        :param node: The current node.

        :type node: ast.ClassDef

        .. todo::
            Add arguments, inherits, and decorators metadata to symbols.
        """

        pos = self.block_position(node)

        if node.name not in self.symbols['classes']:
            self.symbols['classes'][node.name] = {'assignments': [], 'uses': []}
        self.symbols['classes'][node.name]['assignments'].append(pos)

        self.generic_visit(node)

    def visit_Name(self, node):
        self.cache.append(node.id)

    def visit_Attribute(self, node):
        self.visit(node.value)
        self.cache.append(node.attr)

    def visit_Import(self, node):
        pos = self.block_position(node)
        # look through aliases

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

    walker = _TreeWalker()
    walker.visit(tree)
    return walker.symbols

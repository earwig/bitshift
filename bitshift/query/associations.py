__all__ = ["BinaryOp", "UnaryOp"]

class _Association(object):
    pass


class BinaryOp(_Association):
    AND = 1
    OR = 2

    def __init__(self, left, right, op):
        self.left = left
        self.right = right
        self.op = op

    def __str__(self):
        ops = {AND: "And", OR: "Or"}
        return "{0}({1}, {2})".format(ops[self.op], self.left, self.right)


class UnaryOp(_Association):
    NOT = 1

    def __init__(self, node, op):
        self.node = node
        self.op = op

    def __str__(self):
        pass

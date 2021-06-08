import re
from abc import ABC, abstractmethod
import operator
from collections import namedtuple


class Node(ABC):
    @abstractmethod
    def accept(self, visitor):
        pass


class BinopNode(Node):
    def __init__(self, name, opfunc, left, right):
        self.name = name
        self.opfunc = opfunc
        self.left = left
        self.right = right

    def accept(self, visitor):
        return visitor.visit_binop(self)


class UniopNode(Node):
    def __init__(self, name, opfunc, right):
        self.name = name
        self.opfunc = opfunc
        self.right = right

    def accept(self, visitor):
        return visitor.visit_uniop(self)


class ValNode(Node):
    def __init__(self, val):
        self.val = val

    def accept(self, visitor):
        return visitor.visit_val(self)


class NodeVisitor:
    def visit_binop(self, binop_node):
        self.visit_other(binop_node)

    def visit_uniop(self, uniop_node):
        self.visit_other(uniop_node)

    def visit_val(self, val_node):
        self.visit_other(val_node)

    def visit_other(self, _node):
        raise NotImplementedError("default visit_other")


class Lispish(NodeVisitor):
    """
    A visitor that prints out a tree as an S expression.
    """

    def visit_binop(self, binop_node):
        return (
            f"({binop_node.name}"
            f" {binop_node.left.accept(self)}"
            f" {binop_node.right.accept(self)})"
        )

    def visit_uniop(self, uniop_node):
        return f"({uniop_node.name} {uniop_node.right.accept(self)})"

    def visit_val(self, val_node):
        return str(val_node.val)

    def visit_other(self, node):
        return repr(node)


class EvalVisitor(NodeVisitor):
    """
    A visitor that numerically evaluates a tree
    """

    def visit_binop(self, binop_node):
        return binop_node.opfunc(
            binop_node.left.accept(self), binop_node.right.accept(self)
        )

    def visit_uniop(self, uniop_node):
        return uniop_node.opfunc(uniop_node.right.accept(self))

    def visit_val(self, val_node):
        return val_node.val

    def visit_other(self, node):
        raise ValueError(f"Can't evaluate {node}")


OpInfo = namedtuple("OpInfo", ["func", "left_precedence", "right_precedence"])
OPERATORS = {
    "|": OpInfo(operator.or_, 1, 2),
    "^": OpInfo(operator.xor, 3, 4),
    "&": OpInfo(operator.and_, 5, 6),
    ">>": OpInfo(operator.rshift, 7, 8),
    "<<": OpInfo(operator.lshift, 7, 8),
    "+": OpInfo(operator.add, 9, 10),
    "-": OpInfo(operator.sub, 9, 10),
    "*": OpInfo(operator.mul, 11, 12),
    "/": OpInfo(operator.truediv, 11, 12),
    "%": OpInfo(operator.mod, 11, 12),
    "_+": OpInfo(operator.pos, 14, 13),
    "_-": OpInfo(operator.neg, 14, 13),
    "_~": OpInfo(operator.inv, 14, 13),
    "**": OpInfo(operator.pow, 14, 13),
}

MIN_PRECEDENCE = 1
MAX_PRECEDENCE = 14
LEX_RE = re.compile(
    r"(?:(?P<op>\*\*|~|"
    + "|".join(re.escape(x) for x in OPERATORS if not x.startswith("_"))
    + r")|(?P<num>\d+\b)|(?P<paren>[()])|(?P<lexerr>\w+|\S))"
)


class Lexer:
    """
    Simple single-regex lexer
    """
    def __init__(self, instr):
        self._tokens = list(LEX_RE.finditer(instr))

    def clear_for_error(self):
        for tok in self._tokens:
            if tok.group("lexerr"):
                raise ValueError(
                    f"Unrecognized token {tok.group('lexerr')} at {tok.start()}"
                )

    def peek(self):
        if self._tokens:
            return self._tokens[0]
        return None

    def poll(self):
        if self._tokens:
            return self._tokens.pop(0)
        return None

    def __bool__(self):
        return bool(self._tokens)

    def __iter__(self):
        lexer_self = self

        class Iterator:
            def __next__(self):
                retval = lexer_self.poll()
                if retval is not None:
                    return retval
                raise StopIteration

        return Iterator()

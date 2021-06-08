import re
import readline  # not used directly, but its import affects input() in do_main
from abc import ABC, abstractmethod
import operator
from collections import namedtuple
from enum import Enum


class EvalTree(ABC):
    @abstractmethod
    def calc(self):
        pass

    # Uncomment to see tree elems getting created
    #
    # def __init_subclass__(cls, **kwargs):
    #     super().__init_subclass__(**kwargs)
    #     def newinit(oldinit):
    #         def initwrapper(slf, *args):
    #             print(f"{cls.__name__}{tuple(args)}")
    #             oldinit(slf, *args)
    #         return initwrapper
    #     cls.__init__ = newinit(cls.__init__)


class EvalBinop(EvalTree):
    def __init__(self, opfunc, left, right):
        self.opfunc = opfunc
        self.left = left
        self.right = right

    def calc(self):
        return self.opfunc(self.left.calc(), self.right.calc())


class EvalUniop(EvalTree):
    def __init__(self, opfunc, right):
        self.opfunc = opfunc
        self.right = right

    def calc(self):
        return self.opfunc(self.right.calc())


class EvalVal(EvalTree):
    def __init__(self, val):
        self.val = val

    def calc(self):
        return self.val


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
    r"\s*(?:(?P<op>\*\*|~|"
    + "|".join(re.escape(x) for x in OPERATORS if not x.startswith("_"))
    + r")|(?P<num>\d+)|(?P<paren>[()])|(?P<lexerr>\S))\s*"
)


def drive_parse(strategy, exprstr):
    try:
        tokens = list(LEX_RE.finditer(exprstr))
        for tok in tokens:
            if tok.group("lexerr"):
                raise ValueError(
                    f"Unrecognized token {tok.group('lexerr')} at {tok.start()}"
                )
        tree = strategy(tokens)
        return tree.calc()
    except ValueError as err:
        return err


def prattparse(tokstream):
    retval = prattparse_expr(tokstream, MIN_PRECEDENCE - 1)
    if tokstream:
        raise ValueError(f"Expected operator at {tokstream[0].start()}")
    return retval


def prattparse_expr(tokstream, min_prec):
    if not tokstream:
        raise ValueError("Unexpected EOF")
    tok = tokstream.pop(0)
    if tok.group("num"):
        lhs = EvalVal(int(tok.group("num")))
    elif tok.group("paren") and tok.group("paren") == "(":
        lhs = prattparse_expr(tokstream, MIN_PRECEDENCE - 1)
        if tokstream:
            if tokstream[0].group("paren") == ")":
                tokstream.pop(0)
            else:
                raise ValueError(
                    f"Expected operator or right paren at {tokstream[0].start()}"
                )
        else:
            raise ValueError(f"Unclosed left paren beginning at {tok.start()}")
    elif tok.group("paren"):
        raise ValueError(f"Unexpected right paren at {tok.start()}")
    elif tok.group("op"):
        # better be a uniop
        if "_" + tok.group("op") not in OPERATORS:
            raise ValueError(
                "Unknown unary operator %s at %d" % (tok.group("op"), tok.start("op"))
            )
        opinfo = OPERATORS["_" + tok.group("op")]
        rhs = prattparse_expr(tokstream, opinfo.right_precedence)
        lhs = EvalUniop(opinfo.func, rhs)

    while tokstream:
        tok = tokstream[0]
        if not tok.group("op"):
            break
        opinfo = OPERATORS[tok.group("op")]
        if opinfo.left_precedence < min_prec:
            break
        tokstream.pop(0)
        rhs = prattparse_expr(tokstream, opinfo.right_precedence)
        lhs = EvalBinop(opinfo.func, lhs, rhs)

    return lhs


class TokState(Enum):
    "We use this in the shunting yard algorithm"
    EXPECT_OP = 1  # expecting binop or rparen
    EXPECT_ATOM = 2  # expecting num or uniop


def shunting_yard(tokstream):
    val_stack = []

    def binop(func):
        def retval():
            val_stack[-2:] = [EvalBinop(func, val_stack[-2], val_stack[-1])]

        return retval

    def uniop(func):
        def retval():
            val_stack[-1:] = [EvalUniop(func, val_stack[-1])]

        return retval

    def pushval(val):
        def retval():
            val_stack.append(EvalVal(int(val)))

        return retval

    def lparen_error(loc):
        def retval():
            raise ValueError(f"Unclosed left paren beginning at {loc}")

        return retval

    func_stack = []
    tok_state = TokState.EXPECT_ATOM
    for tok in tokstream:
        if tok_state == TokState.EXPECT_ATOM:
            if tok.group("num"):
                to_push = (MAX_PRECEDENCE + 2, pushval(tok.group("num")))
                new_prec = MAX_PRECEDENCE + 1
                tok_state = TokState.EXPECT_OP
            elif tok.group("paren") and tok.group("paren") == "(":
                to_push = (MIN_PRECEDENCE - 1, lparen_error(tok.start()))
                func_stack.append(to_push)
                continue
            elif tok.group("paren"):
                raise ValueError(f"Unexpected right paren at {tok.start()}")
            elif tok.group("op"):
                # better be a uniop
                if "_" + tok.group("op") not in OPERATORS:
                    raise ValueError(
                        "Unknown unary operator %s at %d"
                        % (tok.group("op"), tok.start("op"))
                    )
                opinfo = OPERATORS["_" + tok.group("op")]
                to_push = (opinfo.right_precedence, uniop(opinfo.func))
                new_prec = opinfo.left_precedence
        elif tok_state == TokState.EXPECT_OP:
            if tok.group("op"):
                opinfo = OPERATORS[tok.group("op")]
                to_push = (opinfo.right_precedence, binop(opinfo.func))
                new_prec = opinfo.left_precedence
                tok_state = TokState.EXPECT_ATOM
            else:
                while func_stack:
                    if func_stack[-1][0] == MIN_PRECEDENCE - 1:
                        func_stack.pop()
                        break
                    _, todo = func_stack.pop()
                    todo()
                else:
                    raise ValueError(f"Expected operator at {tok.start()}")
                if tok.group("paren") and tok.group("paren") == ")":
                    continue
                raise ValueError(f"Expected operator or right paren at {tok.start()}")
        while func_stack and new_prec < func_stack[-1][0]:
            _, todo = func_stack.pop()
            todo()
        func_stack.append(to_push)
    if tok_state == TokState.EXPECT_ATOM:
        raise ValueError("Unexpected EOF")
    while func_stack:
        _, todo = func_stack.pop()
        todo()
    assert len(val_stack) == 1, f"Val stack should have length 1, was {val_stack}"
    return val_stack[0]


def prattparse_nopeek(tokstream):
    (retval, next_tok) = prattparse_expr_nopeek(tokstream, MIN_PRECEDENCE - 1)
    if next_tok is not None:
        raise ValueError(f"Expected operator at {next_tok.start()}")
    return retval


def prattparse_expr_nopeek(tokstream, min_prec):
    if not tokstream:
        raise ValueError("Unexpected EOF")
    tok = tokstream.pop(0)
    if tok.group("num"):
        lhs = EvalVal(int(tok.group("num")))
    elif tok.group("paren") and tok.group("paren") == "(":
        (lhs, next_tok) = prattparse_expr_nopeek(tokstream, MIN_PRECEDENCE - 1)
        if next_tok is not None:
            if next_tok.group("paren") == ")":
                pass
            else:
                raise ValueError(
                    f"Expected operator or right paren at {next_tok.start()}"
                )
        else:
            raise ValueError(f"Unclosed left paren beginning at {tok.start()}")
    elif tok.group("paren"):
        raise ValueError(f"Unexpected right paren at {tok.start()}")
    elif tok.group("op"):
        # better be a uniop
        if "_" + tok.group("op") not in OPERATORS:
            raise ValueError(
                "Unknown unary operator %s at %d" % (tok.group("op"), tok.start("op"))
            )
        opinfo = OPERATORS["_" + tok.group("op")]
        rhs = prattparse_expr_nopeek(tokstream, opinfo.right_precedence)
        lhs = EvalUniop(opinfo.func, rhs)

    if not tokstream:
        return (lhs, None)

    tok = tokstream.pop(0)
    while tok is not None:
        if not tok.group("op"):
            break
        opinfo = OPERATORS[tok.group("op")]
        if opinfo.left_precedence < min_prec:
            break
        (rhs, tok) = prattparse_expr_nopeek(tokstream, opinfo.right_precedence)
        lhs = EvalBinop(opinfo.func, lhs, rhs)

    return (lhs, tok)


def do_main():
    try:
        while True:
            instr = input("> ")
            print(f"Pratt parsing gives: {drive_parse(prattparse, instr)}")
            print(f"Shunting yard gives: {drive_parse(shunting_yard, instr)}")
            print(
                f"nopeek Pratt parsing gives: {drive_parse(prattparse_nopeek, instr)}"
            )
    except EOFError:
        print()


if __name__ == "__main__":
    do_main()

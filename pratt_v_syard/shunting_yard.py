"""
Shunting yard parsing module
"""
from enum import Enum
from .op_base import (
    BinopNode,
    UniopNode,
    ValNode,
    MAX_PRECEDENCE,
    MIN_PRECEDENCE,
    OPERATORS,
)


class TokState(Enum):
    "We use this in the shunting yard algorithm"
    EXPECT_OP = 1  # expecting binop or rparen
    EXPECT_ATOM = 2  # expecting num or uniop


def parse(tokstream):
    """
    Parse according to a shunting yard algorithm.

    This doesn't use an output queue, but instead evaluates operations immediately
    when they would hit the output queue.
    """
    val_stack = []

    def binop(name, func):
        def retval():
            val_stack[-2:] = [BinopNode(name, func, val_stack[-2], val_stack[-1])]

        return retval

    def uniop(name, func):
        def retval():
            val_stack[-1:] = [UniopNode(name, func, val_stack[-1])]

        return retval

    def pushval(val):
        def retval():
            val_stack.append(ValNode(int(val)))

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
                opname = "_" + tok.group("op")
                if opname not in OPERATORS:
                    raise ValueError(
                        "Unknown unary operator %s at %d"
                        % (tok.group("op"), tok.start("op"))
                    )
                opinfo = OPERATORS[opname]
                to_push = (
                    opinfo.right_precedence,
                    uniop(opname, opinfo.func),
                )
                new_prec = opinfo.left_precedence
        elif tok_state == TokState.EXPECT_OP:
            if tok.group("op"):
                opinfo = OPERATORS[tok.group("op")]
                to_push = (opinfo.right_precedence, binop(tok.group("op"), opinfo.func))
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

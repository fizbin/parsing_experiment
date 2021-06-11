from .op_base import (
    BinopNode,
    UniopNode,
    ValNode,
    MIN_PRECEDENCE,
    OPERATORS,
)


def parse(tokstream):
    val_stack = []
    prattparse_expr(tokstream, MIN_PRECEDENCE - 1, val_stack)
    tok = tokstream.poll()
    if tok is not None:
        raise ValueError(f"Expected operator at {tok.start()}")
    assert len(val_stack) == 1
    return val_stack[0]


def prattparse_expr(tokstream, min_prec, val_stack):
    tok = tokstream.poll()
    if tok is None:
        raise ValueError("Unexpected EOF")
    if tok.group("num"):
        val_stack.append(ValNode(int(tok.group("num"))))
    elif tok.group("paren") and tok.group("paren") == "(":
        prattparse_expr(tokstream, MIN_PRECEDENCE - 1, val_stack)
        if tokstream:
            tok = tokstream.peek()
            if tok.group("paren") == ")":
                tokstream.poll()
            else:
                raise ValueError(f"Expected operator or right paren at {tok.start()}")
        else:
            raise ValueError(f"Unclosed left paren beginning at {tok.start()}")
    elif tok.group("paren"):
        raise ValueError(f"Unexpected right paren at {tok.start()}")
    elif tok.group("op"):
        # better be a uniop
        opname = "_" + tok.group("op")
        if opname not in OPERATORS:
            raise ValueError(
                "Unknown unary operator %s at %d" % (tok.group("op"), tok.start("op"))
            )
        opinfo = OPERATORS[opname]
        prattparse_expr(tokstream, opinfo.right_precedence, val_stack)
        val_stack[-1:] = [UniopNode(opname, opinfo.func, val_stack[-1])]

    while tokstream:
        tok = tokstream.peek()
        if not tok.group("op"):
            break
        opname = tok.group("op")
        opinfo = OPERATORS[opname]
        if opinfo.left_precedence < min_prec:
            break
        tokstream.poll()
        prattparse_expr(tokstream, opinfo.right_precedence, val_stack)
        val_stack[-2:] = [BinopNode(opname, opinfo.func, val_stack[-2], val_stack[-1])]

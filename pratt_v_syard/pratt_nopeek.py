from .op_base import (
    BinopNode,
    UniopNode,
    ValNode,
    MIN_PRECEDENCE,
    OPERATORS,
)


def parse(tokstream):
    (retval, tok) = prattparse_expr(tokstream, MIN_PRECEDENCE - 1)
    if tok is not None:
        raise ValueError(f"Expected operator at {tok.start()}")
    return retval


def prattparse_expr(tokstream, min_prec):
    tok = tokstream.poll()
    if tok is None:
        raise ValueError("Unexpected EOF")
    if tok.group("num"):
        lhs = ValNode(int(tok.group("num")))
        tok = tokstream.poll()
    elif tok.group("paren") and tok.group("paren") == "(":
        loc = tok.start()
        (lhs, tok) = prattparse_expr(tokstream, MIN_PRECEDENCE - 1)
        if tok is not None:
            if tok.group("paren") == ")":
                pass
            else:
                raise ValueError(f"Expected operator or right paren at {tok.start()}")
        else:
            raise ValueError(f"Unclosed left paren beginning at {loc}")
        tok = tokstream.poll()
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
        (rhs, tok) = prattparse_expr(tokstream, opinfo.right_precedence)
        lhs = UniopNode(opname, opinfo.func, rhs)

    while tok is not None:
        if not tok.group("op"):
            break
        opname = tok.group("op")
        opinfo = OPERATORS[opname]
        if opinfo.left_precedence < min_prec:
            break
        (rhs, tok) = prattparse_expr(tokstream, opinfo.right_precedence)
        lhs = BinopNode(opname, opinfo.func, lhs, rhs)

    return (lhs, tok)

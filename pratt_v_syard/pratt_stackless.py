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
    do_first_part = True
    local_stack = [(min_prec, lambda _l, _t: (_l, _t))]
    while local_stack:
        if do_first_part:
            tok = tokstream.poll()
            if tok is None:
                raise ValueError("Unexpected EOF")
            if tok.group("num"):
                lhs = ValNode(int(tok.group("num")))
                tok = tokstream.poll()
            elif tok.group("paren") and tok.group("paren") == "(":
                loc = tok.start()
                def cpsfunc1_closure(loc_):
                    def cpsfunc1(lhs_, tok_):
                        if tok_ is not None:
                            if tok_.group("paren") == ")":
                                pass
                            else:
                                raise ValueError(
                                    f"Expected operator or right paren at {tok_.start()}")
                        else:
                            raise ValueError(f"Unclosed left paren beginning at {loc_}")
                        return (lhs_, tokstream.poll())
                    return cpsfunc1
                local_stack.append((MIN_PRECEDENCE - 1, cpsfunc1_closure(loc)))
                continue
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
                def cpsfunc2_closure(opname_, opinfo_):
                    def cpsfunc2(rhs_, tok_):
                        return (UniopNode(opname_, opinfo_.func, rhs_), tok_)
                    return cpsfunc2
                local_stack.append((opinfo.right_precedence, cpsfunc2_closure(opname, opinfo)))
                continue

        if tok is not None:
            if not tok.group("op"):
                pass
            else:
                opname = tok.group("op")
                opinfo = OPERATORS[opname]
                if opinfo.left_precedence < local_stack[-1][0]:
                    pass
                else:
                    def cpsfunc3_closure(opname_, opinfo_, lhs_):
                        def cpsfunc3(rhs_, tok_):
                            return (BinopNode(opname_, opinfo_.func, lhs_, rhs_), tok_)
                        return cpsfunc3
                    local_stack.append(
                        (opinfo.right_precedence, cpsfunc3_closure(opname, opinfo, lhs)))
                    do_first_part = True
                    continue

        do_first_part = False
        _, lhs_tok_func = local_stack.pop()
        (lhs, tok) = lhs_tok_func(lhs, tok)

    return (lhs, tok)

from .op_base import (
    BinopNode,
    UniopNode,
    ValNode,
    MIN_PRECEDENCE,
    OPERATORS,
)


def parse(tokstream):
    do_first_part = True
    local_stack = [(MIN_PRECEDENCE - 1, lambda _l: _l, -1)]
    for tok in tokstream:
        if do_first_part:
            if tok.group("num"):
                lhs = ValNode(int(tok.group("num")))
                do_first_part = False
                continue
            if tok.group("paren") and tok.group("paren") == "(":
                local_stack.append((MIN_PRECEDENCE - 1, lambda x: x, tok.start()))
                continue
            if tok.group("paren"):
                raise ValueError(f"Unexpected right paren at {tok.start()}")
            if tok.group("op"):
                # better be a uniop
                opname = "_" + tok.group("op")
                if opname not in OPERATORS:
                    raise ValueError(
                        "Unknown unary operator %s at %d"
                        % (tok.group("op"), tok.start("op"))
                    )
                opinfo = OPERATORS[opname]

                def cpsfunc2_closure(opname_, opinfo_):
                    def cpsfunc2(rhs_):
                        return UniopNode(opname_, opinfo_.func, rhs_)

                    return cpsfunc2

                local_stack.append(
                    (
                        opinfo.right_precedence,
                        cpsfunc2_closure(opname, opinfo),
                        tok.start(),
                    )
                )
                continue
        else:
            if not tok.group("op"):
                while local_stack:
                    old_prec, lhs_func, loc = local_stack.pop()
                    if old_prec == MIN_PRECEDENCE - 1 and loc >= 0:
                        break  # dug back to a left paren, so tok better be an right paren
                    lhs = lhs_func(lhs)
                else:
                    raise ValueError(f"Expected operator at {tok.start()}")
                # can get here only if we hit 'break' 4 lines up, so require right paren
                if tok.group("paren") == ")":
                    continue
                raise ValueError(f"Expected operator or right paren at {tok.start()}")

            # Now know that tok is an op
            opname = tok.group("op")
            opinfo = OPERATORS[opname]
            while opinfo.left_precedence < local_stack[-1][0]:
                _, lhs_func, _ = local_stack.pop()
                lhs = lhs_func(lhs)

            def cpsfunc3_closure(opname_, opinfo_, lhs_):
                def cpsfunc3(rhs_):
                    return BinopNode(opname_, opinfo_.func, lhs_, rhs_)

                return cpsfunc3

            local_stack.append(
                (
                    opinfo.right_precedence,
                    cpsfunc3_closure(opname, opinfo, lhs),
                    tok.start(),
                )
            )
            do_first_part = True

    if do_first_part:
        raise ValueError("Unexpected EOF")

    while local_stack:
        old_prec, lhs_func, loc = local_stack.pop()
        if old_prec == MIN_PRECEDENCE - 1 and loc >= 0:
            raise ValueError(f"Unclosed left paren beginning at {loc}")
        lhs = lhs_func(lhs)

    return lhs

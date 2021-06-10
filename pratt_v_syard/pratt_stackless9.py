from .op_base import (
    BinopNode,
    UniopNode,
    ValNode,
    MIN_PRECEDENCE,
    OPERATORS,
)


def parse(tokstream):
    def cpsfunc1_closure(loc):
        def cpsfunc1(lhs_):
            raise ValueError(f"Unclosed left paren beginning at {loc}")

        return cpsfunc1

    def cpsfunc2_closure(opname_, opinfo_):
        def cpsfunc2(rhs_):
            return UniopNode(opname_, opinfo_.func, rhs_)

        return cpsfunc2

    def cpsfunc3_closure(opname_, opinfo_, lhs_):
        def cpsfunc3(rhs_):
            return BinopNode(opname_, opinfo_.func, lhs_, rhs_)

        return cpsfunc3

    do_first_part = True
    local_stack = [(MIN_PRECEDENCE - 2, lambda _l: _l)]
    for tok in tokstream:
        if do_first_part:
            if tok.group("num"):
                lhs = ValNode(int(tok.group("num")))
                do_first_part = False
            if tok.group("paren") and tok.group("paren") == "(":
                local_stack.append((MIN_PRECEDENCE - 1, cpsfunc1_closure(tok.start())))
            elif tok.group("paren"):
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

                local_stack.append(
                    (
                        opinfo.right_precedence,
                        cpsfunc2_closure(opname, opinfo),
                    )
                )
        else:
            if tok.group("op") is not None:
                opname = tok.group("op")
                opinfo = OPERATORS[opname]
                while opinfo.left_precedence < local_stack[-1][0]:
                    _, lhs_func = local_stack.pop()
                    lhs = lhs_func(lhs)

                local_stack.append(
                    (
                        opinfo.right_precedence,
                        cpsfunc3_closure(opname, opinfo, lhs),
                    )
                )
                do_first_part = True
            else:
                while local_stack:
                    old_prec, lhs_func = local_stack.pop()
                    if old_prec == MIN_PRECEDENCE - 1:
                        break  # dug back to a left paren, so tok better be an right paren
                    lhs = lhs_func(lhs)
                else:
                    raise ValueError(f"Expected operator at {tok.start()}")
                # can get here only if we hit 'break' 4 lines up, so require right paren
                if tok.group("paren") != ")":
                    raise ValueError(
                        f"Expected operator or right paren at {tok.start()}"
                    )

    if do_first_part:
        raise ValueError("Unexpected EOF")

    while local_stack:
        _, lhs_func = local_stack.pop()
        lhs = lhs_func(lhs)

    return lhs

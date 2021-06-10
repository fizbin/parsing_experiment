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
    while local_stack:
        tok = tokstream.poll()
        if do_first_part:
            if tok is None:
                raise ValueError("Unexpected EOF")
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

        if tok is None:
            break

        do_first_part = False
        while (not tok.group("op")) or (
            OPERATORS[tok.group("op")].left_precedence < local_stack[-1][0]
        ):
            if not local_stack:
                break
            old_prec, lhs_func, loc = local_stack.pop()
            if old_prec == MIN_PRECEDENCE - 1 and loc >= 0:
                if tok.group("paren") != ")":
                    raise ValueError(
                        f"Expected operator or right paren at {tok.start()}"
                    )
                # Note that in this case we continue shortly after here, after we
                # verify that we didn't just pop the last thing off the local stack
                break
            lhs = lhs_func(lhs)

        if not local_stack:
            raise ValueError(f"Expected operator at {tok.start()}")

        if tok.group("paren") == ")":
            continue

        opname = tok.group("op")
        opinfo = OPERATORS[opname]

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
        continue

    while local_stack:
        old_prec, lhs_func, loc = local_stack.pop()
        if old_prec == MIN_PRECEDENCE - 1 and loc >= 0:
            raise ValueError(f"Unclosed left paren beginning at {loc}")
        lhs = lhs_func(lhs)

    return lhs

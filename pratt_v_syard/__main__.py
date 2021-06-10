"""
Simple main for interactive parser testing
"""
import readline  # noqa pylint:disable=unused-import
from .parsers import PARSERS, drive_parse
from .op_base import EvalVisitor, Lispish


def display(parse_name, parse_func, exprstr):
    try:
        tree = drive_parse(parse_func, exprstr)
        print(f"{parse_name} evaluated to {tree.accept(EvalVisitor())}")
        print(f"   s-exp: {tree.accept(Lispish())}")
    except (ValueError, ZeroDivisionError) as err:
        print(f"{parse_name} errored: {err}")


try:
    while True:
        instr = input("> ")
        for (nom, func) in PARSERS:
            display(nom, func, instr)
except EOFError:
    print()

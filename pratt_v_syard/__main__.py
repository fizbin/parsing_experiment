"""
Simple main for parser testing
"""
import readline  #noqa pylint:disable=unused-import
from .shunting_yard import parse as sy_parse
from .basic_pratt import parse as pratt1_parse
from .pratt_nopeek import parse as pratt2_parse
from .op_base import Lexer, EvalVisitor, Lispish

PARSERS = (
    ("Shunting Yard", sy_parse),
    ("Basic Pratt Parsing", pratt1_parse),
    ("No-peek Pratt Parsing", pratt2_parse),
    )

def drive_parse(strategy, exprstr):
    tokens = Lexer(exprstr)
    tokens.clear_for_error()
    return strategy(tokens)

def display(parse_name, parse_func, exprstr):
    try:
        tree = drive_parse(parse_func, exprstr)
        print(f"{parse_name} evaluated to {tree.accept(EvalVisitor())}")
        print(f"   s-exp: {tree.accept(Lispish())}")
    except ValueError as err:
        print(f"{parse_name} errored: {err}")


try:
    while True:
        instr = input("> ")
        for (nom, func) in PARSERS:
            display(nom, func, instr)
except EOFError:
    print()

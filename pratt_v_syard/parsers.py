"""
Exports PARSERS which connects to all the parsers
"""
from .shunting_yard import parse as sy_parse
from .basic_pratt import parse as pratt1_parse
from .pratt_nopeek import parse as pratt2_parse
from .op_base import Lexer

PARSERS = (
    ("Shunting Yard", sy_parse),
    ("Basic Pratt Parsing", pratt1_parse),
    ("No-peek Pratt Parsing", pratt2_parse),
    )


def drive_parse(strategy, exprstr):
    tokens = Lexer(exprstr)
    tokens.clear_for_error()
    return strategy(tokens)

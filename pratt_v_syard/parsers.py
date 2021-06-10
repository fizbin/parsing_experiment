"""
Exports PARSERS which connects to all the parsers
"""
from .shunting_yard import parse as sy_parse
from .basic_pratt import parse as pratt1_parse
from .pratt_nopeek import parse as pratt2_parse
from .pratt_stackless import parse as pratt_sl1_parse
from .pratt_stackless2 import parse as pratt_sl2_parse
from .pratt_stackless3 import parse as pratt_sl3_parse
from .pratt_stackless4 import parse as pratt_sl4_parse
from .op_base import Lexer

PARSERS = (
    ("Shunting Yard", sy_parse),
    ("Basic Pratt Parsing", pratt1_parse),
    ("No-peek Pratt Parsing", pratt2_parse),
    ("Stackless Pratt Parsing", pratt_sl1_parse),
    ("Stackless2 Pratt Parsing", pratt_sl2_parse),
    ("Stackless3 Pratt Parsing", pratt_sl3_parse),
    ("Stackless4 Pratt Parsing", pratt_sl4_parse),
)


def drive_parse(strategy, exprstr):
    tokens = Lexer(exprstr)
    tokens.clear_for_error()
    return strategy(tokens)

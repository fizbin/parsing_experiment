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
from .pratt_stackless5 import parse as pratt_sl5_parse
from .pratt_stackless6 import parse as pratt_sl6_parse
from .pratt_stackless7 import parse as pratt_sl7_parse
from .pratt_stackless8 import parse as pratt_sl8_parse
from .pratt_stackless9 import parse as pratt_sl9_parse
from .op_base import Lexer

PARSERS = (
    ("Shunting Yard", sy_parse),
    ("Basic Pratt Parsing", pratt1_parse),
    ("No-peek Pratt Parsing", pratt2_parse),
    ("Stackless Pratt Parsing", pratt_sl1_parse),
    ("Stackless2 Pratt Parsing", pratt_sl2_parse),
    ("Stackless3 Pratt Parsing", pratt_sl3_parse),
    ("Stackless4 Pratt Parsing", pratt_sl4_parse),
    ("Stackless5 Pratt Parsing (just one poll)", pratt_sl5_parse),
    ("Stackless6 Pratt Parsing (iter, not poll)", pratt_sl6_parse),
    ("Stackless7 Pratt Parsing", pratt_sl7_parse),
    ("Stackless8 Pratt Parsing", pratt_sl8_parse),
    ("Stackless9 Pratt Parsing", pratt_sl9_parse),
)


def drive_parse(strategy, exprstr):
    tokens = Lexer(exprstr)
    tokens.clear_for_error()
    return strategy(tokens)

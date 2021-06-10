"""
Simple unittest to test each parser error case and some standard tests
"""

import re
import unittest

from .parsers import PARSERS, drive_parse
from .op_base import Lispish


class TestParseErrors(unittest.TestCase):
    def do_error_test_case(self, inputstr, errorstr):
        for (pname, pfunc) in PARSERS:
            with self.subTest(pname, expr=inputstr):
                with self.assertRaisesRegex(ValueError, re.escape(errorstr)):
                    drive_parse(pfunc, inputstr)

    def test_expected_operator(self):
        self.do_error_test_case("4 + 5 9", "Expected operator at 6")
        self.do_error_test_case("4 + 5 )", "Expected operator at 6")
        self.do_error_test_case("4 + 5 (", "Expected operator at 6")

    def test_unexpected_eof(self):
        self.do_error_test_case("4 + 5 *", "Unexpected EOF")
        self.do_error_test_case("4 + 5 - -", "Unexpected EOF")
        self.do_error_test_case("4 + 5 - ~ -", "Unexpected EOF")

    def test_expected_op_or_rparen(self):
        self.do_error_test_case("(4 + 5 (", "Expected operator or right paren at 7")
        self.do_error_test_case("(4 + 5 3", "Expected operator or right paren at 7")

    def test_unclosed_lparen(self):
        self.do_error_test_case("(4 + 5", "Unclosed left paren beginning at 0")
        self.do_error_test_case("4 + (5", "Unclosed left paren beginning at 4")
        self.do_error_test_case("(4 + (5", "Unclosed left paren beginning at 5")
        self.do_error_test_case("(4 * (5 - 3)", "Unclosed left paren beginning at 0")

    def test_unexpected_rparen(self):
        self.do_error_test_case("4 + )5", "Unexpected right paren at 4")

    def test_unknown_unary_operator(self):
        self.do_error_test_case("4 + & 5", "Unknown unary operator & at 4")

    def test_basic_success(self):
        for (pname, pfunc) in PARSERS:
            with self.subTest(pname):
                actual = drive_parse(pfunc, "2**3**2").accept(Lispish())
                self.assertEqual(actual, "(** 2 (** 3 2))")
                actual = drive_parse(pfunc, "( 2   ** 3 ) ** 2").accept(Lispish())
                self.assertEqual(actual, "(** (** 2 3) 2)")
                actual = drive_parse(pfunc, "-2**-3").accept(Lispish())
                self.assertEqual(actual, "(_- (** 2 (_- 3)))")

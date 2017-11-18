from unittest import TestCase

from dropSQL.parser.tokens import *
from dropSQL.parser.rules import *


class TokenStreamTestCase(TestCase):
    def test_basic(self):
        ts = TokenStream(Stream('/select 5 /drop'))
        # @formatter:off
        self.assertIsInstance(ts.gettok().ok(), Select)
        self.assertEqual     (ts.gettok().ok(), Integer(5))
        self.assertIsInstance(ts.gettok().ok(), Drop)
        self.assertTrue      (ts.gettok().is_err())
        # @formatter:on

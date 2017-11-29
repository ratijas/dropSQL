from unittest import TestCase

from dropSQL.ast import *
from dropSQL.parser.streams import *


class TyTestCase(TestCase):
    def test(self):
        self.assertIsInstance(Ty.from_sql(Tokens.from_str('integer')).ok(), IntegerTy)
        self.assertIsInstance(Ty.from_sql(Tokens.from_str('float')).ok(), FloatTy)
        self.assertIsInstance(Ty.from_sql(Tokens.from_str('varchar(15)')).ok(), VarCharTy)
        self.assertFalse(Ty.from_sql(Tokens.from_str('varchar 10')))
        self.assertTrue(Ty.from_sql(Tokens.from_str('varchar(')).err().is_incomplete())

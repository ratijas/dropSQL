from unittest import TestCase

from dropSQL.ast import *
from dropSQL.parser.rules import Ty
from dropSQL.parser.tokens import TokenStream, Stream


class TyTestCase(TestCase):
    def test(self):
        self.assertIsInstance(Ty.parse(TokenStream(Stream('integer'))).ok(), IntegerTy)
        self.assertIsInstance(Ty.parse(TokenStream(Stream('float'))).ok(), FloatTy)
        self.assertIsInstance(Ty.parse(TokenStream(Stream('varchar(15)'))).ok(), VarCharTy)
        self.assertFalse(Ty.parse(TokenStream(Stream('varchar 10'))))

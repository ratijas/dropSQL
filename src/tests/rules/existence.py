from unittest import TestCase

from dropSQL.ast import *
from dropSQL.parser.rules import *
from dropSQL.parser.tokens import Stream, TokenStream


class ExistenceTestCase(TestCase):
    def test(self):
        res = Existence.parse(TokenStream(Stream('/IF EXISTS')))
        self.assertTrue(res)
        self.assertIsNotNone(res.ok())

        res = Existence.parse(TokenStream(Stream('')))
        self.assertTrue(res)
        self.assertIsNone(res.ok())

        res = Existence.parse(TokenStream(Stream('if file')))
        self.assertFalse(res)


class NonExistenceTestCase(TestCase):
    def test(self):
        res = NonExistence.parse(TokenStream(Stream('/if /not EXISTS')))
        self.assertTrue(res)
        self.assertIsNotNone(res.ok())

        res = NonExistence.parse(TokenStream(Stream('if file')))
        self.assertFalse(res)

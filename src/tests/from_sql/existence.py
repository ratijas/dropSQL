from unittest import TestCase

from dropSQL.ast import *
from dropSQL.generic import *
from dropSQL.parser.streams import *


class ExistenceTestCase(TestCase):
    def test(self) -> None:
        tokens = Tokens.from_str('/if exists')
        res = IfExists.from_sql(tokens)
        self.assertTrue(res)
        self.assertIsNotNone(res.ok())

        tokens = Tokens.from_str('/if not exists person')
        res = IfNotExists.from_sql(tokens)
        self.assertTrue(res)
        self.assertIsNotNone(res.ok())
        t = tokens.next().and_then(Cast(Identifier))
        self.assertTrue(t)
        self.assertEqual(t.ok(), Identifier('person'))

        tokens = Tokens.from_str('person')
        res = IfNotExists.from_sql(tokens)
        self.assertTrue(res)
        self.assertIsNone(res.ok())

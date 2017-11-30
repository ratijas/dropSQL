from unittest import TestCase

from dropSQL.ast import *
from dropSQL.parser.streams import *


class DeleteFromTestCase(TestCase):
    def test(self) -> None:
        sql = '/delete from matrix /drop  -- clear table `matrix`'
        t = DeleteFrom.from_sql(Tokens.from_str(sql))
        self.assertTrue(t)
        self.assertEqual(t.ok().table, Identifier('matrix'))
        self.assertIsNone(t.ok().where)

        sql = '/delete from /friends /where 1 /= 2 /drop'
        t = DeleteFrom.from_sql(Tokens.from_str(sql))
        self.assertTrue(t)
        self.assertIsNotNone(t.ok().where)
        where = t.ok().where
        self.assertIsInstance(where, ExpressionBinary)

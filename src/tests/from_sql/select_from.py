from unittest import TestCase

from dropSQL.ast import *
from dropSQL.parser.streams import *


class SelectFromTestCase(TestCase):
    def test(self) -> None:
        sql = '/select a /as b, *, c from /d E /where f < E/g /drop'
        t = SelectFrom.from_sql(Tokens.from_str(sql))
        self.assertTrue(t)
        sel = t.ok()

        self.assertEqual(len(sel.columns), 3)
        self.assertEqual(sel.table.name, Identifier('d'))
        self.assertEqual(sel.table.alias, Identifier('E'))

    def test_join(self) -> None:
        sql = '/select * from a, b, c asD /drop'
        t = SelectFrom.from_sql(Tokens.from_str(sql))
        self.assertTrue(t)
        joins = t.ok().joins

        self.assertEqual(len(joins), 2)

        self.assertEqual(joins[0].table.name, Identifier('b'))
        self.assertIsNone(joins[0].table.alias)

        self.assertEqual(joins[1].table.name, Identifier('c'))
        self.assertEqual(joins[1].table.alias, Identifier('asD'))

        sql = '/select * from a /join b c /on a/name = c/id, c d /drop'
        t = SelectFrom.from_sql(Tokens.from_str(sql))
        self.assertTrue(t)
        joins = t.ok().joins

        join_b: InnerJoin = joins[0]
        self.assertEqual(join_b.table.name, Identifier('b'))
        self.assertEqual(join_b.table.alias, Identifier('c'))
        self.assertEqual(join_b.constraint.to_sql(), 'a/name = c/id')

        join_c: CrossJoin = joins[1]
        self.assertEqual(join_c.table.name, Identifier('c'))
        self.assertEqual(join_c.table.alias, Identifier('d'))

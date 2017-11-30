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

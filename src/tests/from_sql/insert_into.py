from unittest import TestCase

from dropSQL.ast import *
from dropSQL.ast.insert_into import CommaSeparated, IdentFromSQL
from dropSQL.parser.streams import *


class InsertIntoTestCase(TestCase):
    def test(self) -> None:
        sql = '/insert into t (a, b) values (?1, ?1*2), (?2, ?2/2), (\'hello\', 42) /drop'
        t = InsertInto.from_sql(Tokens.from_str(sql))
        self.assertTrue(t)
        i = t.ok()
        self.assertEqual(len(i.values), 3)

    def test_separated(self) -> None:
        sql = 'a, b, c'
        ts = Tokens.from_str(sql)
        cs = CommaSeparated(IdentFromSQL, ts)
        tokens = cs.collect().ok()
        self.assertEqual(3, len(tokens))

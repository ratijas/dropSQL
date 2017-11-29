from unittest import TestCase

from dropSQL.ast import *
from dropSQL.parser.streams import *


class InsertIntoTestCase(TestCase):
    def test(self) -> None:
        sql = '/insert into t (a, b) values (?1, ?1*2), (?2, ?2/2), (\'hello\', 42) /drop'
        t = InsertInto.from_sql(Tokens.from_str(sql))
        self.assertTrue(t)
        i = t.ok()
        self.assertEqual(len(i.values), 3)

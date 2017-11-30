from unittest import TestCase

from dropSQL.ast.comma_separated import CommaSeparated
from dropSQL.ast.insert_into import IdentFromSQL
from dropSQL.parser.streams import *


class InsertIntoTestCase(TestCase):
    def test(self) -> None:
        sql = 'a, b, c'
        ts = Tokens.from_str(sql)
        cs = CommaSeparated(IdentFromSQL, ts)
        tokens = cs.collect().ok()
        self.assertEqual(3, len(tokens))

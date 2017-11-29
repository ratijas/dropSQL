from unittest import TestCase

from dropSQL.ast import *
from dropSQL.parser.streams import *


class DropTableTestCase(TestCase):
    def test(self) -> None:
        tokens = Tokens.from_str('/drop table /if exists person /drop\n/drop')
        res = DropTable.from_sql(tokens)
        self.assertTrue(res)

        res = DropTable.from_sql(tokens)
        self.assertFalse(res)
        self.assertTrue(res.err().is_incomplete())

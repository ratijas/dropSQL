from unittest import TestCase

from dropSQL.ast import *
from dropSQL.parser.streams import *


class CreateTableTestCase(TestCase):
    def test(self):
        sql = (
            '/create table /person (\n'
            '    /name varchar(42),\n'
            '    /age integer,\n'
            ') /drop')
        res = CreateTable.from_sql(Tokens.from_str(sql))

        self.assertTrue(res)
        table = res.ok()

        self.assertFalse(table.if_not_exists)
        self.assertEqual(table.table, Identifier('person'))
        self.assertEqual(2, len(table.columns))

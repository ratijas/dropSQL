from unittest import TestCase

from dropSQL.parser.tokens import *
from dropSQL.ast import *


class AstTestCase(TestCase):
    def test_create_table(self):
        ct = CreateTable(True, Identifier('person', True), [
            ColumnDef(Identifier('name', False), VarCharTy(32), True),
            ColumnDef(Identifier('age', False), IntegerTy(), False),
            ColumnDef(Identifier('height', False), FloatTy(), False),
        ])
        sql = ct.to_sql()
        expected = (
            '/create table if not exists /person (\n'
            '\tname varchar(32) /primary key,\n'
            '\tage integer,\n'
            '\theight float,\n'
            ') /drop'
        )
        self.assertEqual(expected, sql)

from unittest import TestCase

from dropSQL.parser.tokens import *
from dropSQL.ast import *


class AstTestCase(TestCase):
    def test_literal(self):
        self.assertEqual('float', FloatTy().to_sql())
        self.assertEqual('integer', IntegerTy().to_sql())
        self.assertEqual('varchar(42)', VarCharTy(42).to_sql())

    def test_column_def(self):
        self.assertEqual('/name varchar(42) /primary key,',
                         ColumnDef(Identifier('name', True), VarCharTy(42), True).to_sql())
        self.assertEqual('age integer,',
                         ColumnDef(Identifier('age', False), IntegerTy(), False).to_sql())
        self.assertEqual('height float,',
                         ColumnDef(Identifier('height', False), FloatTy(), False).to_sql())

    def test_create_table(self):
        ct = CreateTable(IfNotExists(), Identifier('person', True), [
            ColumnDef(Identifier('name', False), VarCharTy(42), True),
            ColumnDef(Identifier('age', True), IntegerTy(), False),
            ColumnDef(Identifier('height', False), FloatTy(), False),
        ])
        sql = ct.to_sql()
        expected = (
            '/create table if not exists /person (\n'
            '\tname varchar(42) /primary key,\n'
            '\t/age integer,\n'
            '\theight float,\n'
            ') /drop'
        )
        self.assertEqual(expected, sql)

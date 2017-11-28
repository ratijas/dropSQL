from unittest import TestCase

from dropSQL.ast import Ast, CreateTable
from dropSQL.parser.rules import *
from dropSQL.parser.tokens import *


class CreateStmtTestCase(TestCase):
    def test_stmt(self):
        sql = ('/create table /person (\n'
               '    /name varchar(42),\n'
               ') /drop')
        ts = TokenStream(Stream(sql))
        res = CreateStmt.parse(ts)

        self.assertTrue(res)
        table = res.ok()

        self.assertFalse(table.if_not_exists)
        self.assertEqual(table.table, Identifier('person'))
        self.assertEqual(1, len(table.columns))

    def test_no_columns(self):
        sql = '/create table /person ( ) /drop'
        ts = TokenStream(Stream(sql))
        res = CreateStmt.parse(ts)
        self.assertFalse(res)

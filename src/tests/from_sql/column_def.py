from unittest import TestCase

from dropSQL.ast import *
from dropSQL.parser.streams import *


class ColumnDefTestCase(TestCase):
    def test(self):
        sql = '/name varchar(42), /age integer /primary key)'

        res = ColumnDef.from_sql(Tokens.from_str(sql))
        self.assertTrue(res)

        res = CreateTable.parse_columns(Tokens.from_str(sql))
        self.assertTrue(res)
        self.assertEqual(2, len(res.ok()))

        sql = '/age integer /pri'
        res = CreateTable.parse_columns(Tokens.from_str(sql))
        self.assertFalse(res)

        sql = '/file_id integer /primary key,'
        col = ColumnDef.from_sql(Tokens.from_str(sql)).ok()
        self.assertTrue(col.is_primary_key)
        self.assertEqual(col.name, Identifier('file_id'))
        self.assertIsInstance(col.ty, IntegerTy)

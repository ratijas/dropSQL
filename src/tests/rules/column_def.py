from unittest import TestCase

from dropSQL.ast import *
from dropSQL.parser.rules import ColumnsDef, ColumnDef
from dropSQL.parser.tokens import *


class ColumnsDefTestCase(TestCase):
    def test(self):
        sql = '/name varchar(42), '

        res = ColumnDef.parse(TokenStream(Stream(sql)))
        self.assertTrue(res)

        res = ColumnsDef.parse(TokenStream(Stream(sql)))
        self.assertTrue(res)
        self.assertEqual(1, len(res.ok()))

        sql = '/file_id integer /primary key,'
        col = ColumnDef.parse(TokenStream(Stream(sql))).ok()
        self.assertTrue(col.is_primary_key)
        self.assertEqual(col.name, Identifier('file_id'))
        self.assertIsInstance(col.ty, IntegerTy)

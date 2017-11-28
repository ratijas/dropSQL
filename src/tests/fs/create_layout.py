from unittest import TestCase

from dropSQL.ast import ColumnDef, IntegerTy, FloatTy, VarCharTy
from dropSQL.fs.db_file import DBFile
import os
import sys

from dropSQL.fs.table import Table
from dropSQL.parser.tokens.identifier import Identifier
from dropSQL.parser.tokens.literal import Integer, Float, VarChar


class LayoutCase(TestCase):
    def test(self):
        os.remove("test.dropdb")
        open("test.dropdb", "w").close()
        connection = DBFile("test.dropdb")

        db_name = "Database name!"
        metadata = connection.get_metadata()
        metadata.set_name(db_name)
        assert metadata.get_name() == db_name, "Failed to read database name: {}".format(metadata.get_name())
        assert metadata.get_data_blocks_count() == 0, "Initial data blocks count is not zero"

        tables = connection.get_tables()
        for i, table in enumerate(tables):
            table_name = "Table {}!".format(i)
            table.set_table_name(table_name)
            assert table.get_table_name() == table_name, "Failed to read table name"
            table.add_column(ColumnDef(Identifier("int 1"), IntegerTy()))
            table.add_column(ColumnDef(Identifier("int 2"), IntegerTy()))
            table.add_column(ColumnDef(Identifier("float 1"), FloatTy()))
            table.add_column(ColumnDef(Identifier("float 2"), FloatTy()))
            table.add_column(ColumnDef(Identifier("string 1"), VarCharTy(123)))
            table.add_column(ColumnDef(Identifier("string 2"), VarCharTy(321)))
            table.insert({Identifier("int 1")   : Integer(1),
                          Identifier("int 2")   : Integer(2),
                          Identifier("float 1") : Float(2.71),
                          Identifier("float 2") : Float(3.14),
                          Identifier("string 1"): VarChar("meow"),
                          Identifier("string 2"): VarChar("purr")})
            sys.stderr.write(str(table.select(0)))
            # sys.stderr.write('Record count: ' + str(table.count_records()))
            sys.stderr.write(str(table.get_columns()) + "\n")

        connection.close()

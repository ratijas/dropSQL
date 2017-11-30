import sys
from unittest import TestCase

from dropSQL.ast import ColumnDef, IntegerTy, FloatTy, VarCharTy
from dropSQL.fs.db_file import DBFile
from dropSQL.fs.table import Table
from dropSQL.parser.tokens.identifier import Identifier
from dropSQL.parser.tokens.literal import Integer, Float, VarChar


class LayoutCase(TestCase):
    def test(self):
        open("test.dropdb", "w").close()
        connection = DBFile("test.dropdb")

        db_name = "Database name!"
        metadata = connection.get_metadata()
        metadata.set_name(db_name)
        self.assertEqual(metadata.get_name(), db_name,
                         msg="Failed to read database name: {}".format(metadata.get_name()))
        self.assertEqual(metadata.get_data_blocks_count(), 0,
                         msg="Initial data blocks count is not zero")

        tables = connection.get_tables()
        for index, table in enumerate(tables):
            table: Table = table

            table_name = "Table {}!".format(index)
            table.set_table_name(table_name)
            assert table.get_table_name() == table_name, "Failed to read table name"
            table.add_column(ColumnDef(Identifier("ind"), IntegerTy()))
            table.add_column(ColumnDef(Identifier("text"), VarCharTy(15)))
            for i in range(0, 10 ** 3):
                # sys.stderr.write("Inserting record {} into {}\n".format(i, index))
                table.insert({Identifier("ind"): Integer(i),
                              Identifier("text"): VarChar("qwerty123456")})
                if i % 3 == 0:
                    table.delete(i)
                if i % 3 == 1:
                    table.update(i, {Identifier("ind"): Integer(-i),
                                     Identifier("text"): VarChar("123456qwerty")})
                try:
                    values = table.select(i)
                    assert values[0] == i or values[0] == -i, \
                        "received({}): {}".format(i, values[0])
                    assert values[1] == "qwerty123456" or values[1] == "123456qwerty", \
                        "received({}): {}".format(i, values[Identifier("text")])
                except AttributeError:
                    # sys.stderr.write("Record {} is dead\n".format(i))
                    # record deleted
                    # shitty code ♥
                    pass
            sys.stderr.write('Record count: {}\n'.format(table.count_records()))
            sys.stderr.write('{}\n'.format(str(table.get_columns())))
            table.drop()
            break
        sys.stderr.write('Tables: {}\n'.format([t.get_table_name() for t in connection.get_tables()]))

        connection.close()

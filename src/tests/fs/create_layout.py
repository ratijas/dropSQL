import sys
from unittest import TestCase

from dropSQL.ast import ColumnDef, IntegerTy, VarCharTy
from dropSQL.fs.db_file import DBFile
from dropSQL.parser.tokens.identifier import Identifier


class LayoutCase(TestCase):
    def test(self):
        connection = DBFile(":memory:")

        db_name = "Database name!"
        metadata = connection.metadata
        metadata.name = db_name
        self.assertEqual(metadata.name, db_name,
                         msg="Failed to read database name: {}".format(metadata.name))
        self.assertEqual(metadata.data_blocks_count, 0,
                         msg="Initial data blocks count is not zero")

        tables = connection.get_tables()
        for index, table in enumerate(tables):
            table_name = Identifier("Table {}!".format(index))
            table.set_table_name(table_name)
            self.assertEqual(table.get_table_name(), table_name, msg="Failed to read table name")

            table.add_column(ColumnDef(Identifier("ind"), IntegerTy()))
            table.add_column(ColumnDef(Identifier("text"), VarCharTy(15)))
            for i in range(0, 10 ** 4):
                # sys.stderr.write("Inserting record {} into {}\n".format(i, index))
                table.insert([i, "qwerty123456"]).ok()
                if i % 3 == 0: table.delete(i).ok()
                if i % 3 == 1: table.update([-i, "123456qwerty"], i).ok()

                res = table.select(i)
                if not res: continue
                values = res.ok()

                self.assertEqual(abs(values[0]), i,
                                 msg="received({}): {}".format(i, values[0]))
                self.assertIn(values[1], ("qwerty123456", "123456qwerty"),
                              msg="received({}): {}".format(i, values[1]))
            sys.stderr.write('Record count: {}\n'.format(table.count_records()))
            sys.stderr.write('{}\n'.format(str(table.get_columns())))

            table.drop()
            break
        sys.stderr.write('Tables: {}\n'.format([t.get_table_name() for t in connection.get_tables()]))

        connection.close()

from unittest import TestCase

from dropSQL.fs.db_file import DBFile
import os
import sys


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
        for i in range(0, 16):
            table_name = "Table {}!".format(i)
            tables[i].set_table_name(table_name)
            assert tables[i].get_table_name() == table_name, "Failed to read table name"
            tables[i].add_int_column("int column 1")
            tables[i].add_int_column("int column 2")
            tables[i].add_float_column("float column 1")
            tables[i].add_float_column("float column 2")
            tables[i].add_string_column("string column 1", 123)
            tables[i].add_string_column("string column 2", 321)
            tables[i].insert({"int column 1": 1,
                              "int column 2": 2,
                              "float column 1": 2.71,
                              "float column 2": 3.14,
                              "string column 1": "meow",
                              "string column 2": "purr"})
            sys.stderr.write(str(tables[i].select(0)))
            # sys.stderr.write('Record count: ' + str(tables[i].count_records()))
            sys.stderr.write(str(tables[i].get_columns()) + "\n")

        connection.close()

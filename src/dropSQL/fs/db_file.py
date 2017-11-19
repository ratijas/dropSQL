"""
Class for db file i/o
"""

import os
from dropSQL.fs.metadata import Metadata


class DBFile:
    def __init__(self, filename):
        self.db_file = self.setup_with_file(filename)
        self._read_metadata()
        self._read_table_descriptors()

    def setup_with_file(self, filename):
        if os.path.exists(filename):
            return self._open_database(filename)
        else:
            return self._create_database(filename)

    @staticmethod
    def _create_database(filename):
        db_file = open(filename, "r+b")

        return db_file

    @staticmethod
    def _open_database(filename):
        db_file = open(filename, "r+b")
        return db_file

    def _read_metadata(self):
        metadata_block = self._read_block(0)
        self.metadata = Metadata(metadata_block)

    def _read_table_descriptors(self):
        pass

    def _read_block(self, block_num):
        pass

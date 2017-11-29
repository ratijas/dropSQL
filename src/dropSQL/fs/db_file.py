"""
Class for db file i/o
"""

import os
import sys

from dropSQL.fs.block import Block


class DBFile:
    def __init__(self, filename):
        self.filename = filename
        self.file = open(filename, "r+b", 2**23)
        self.file.write(b'\0' * 4096 * 17)

    def get_metadata(self):
        from dropSQL.fs.metadata import Metadata
        return Metadata(self)

    def get_tables(self) -> list:
        from dropSQL.fs.table import Table
        return [Table(self, i) for i in range(0, 16)]

    def read_block(self, block_num) -> Block:
        self.file.seek(4096 * block_num)
        try:
            data = Block(self.file.read(4096))
        except AssertionError:
            raise AssertionError("Block " + str(block_num) + " does not exist")
        return data

    def write_block(self, block_num: int, block: Block):
        self.file.seek(4096 * block_num)
        self.file.write(block.data)

    def allocate_block(self) -> int:
        self.file.seek(0, 2)  # eof
        self.file.write(b'\0' * 4096)
        c = self.get_metadata().get_data_blocks_count()
        self.get_metadata().set_data_blocks_count(c + 1)
        return c + 17

    def close(self):
        self.file.flush()
        self.file.close()

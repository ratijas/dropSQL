"""
Class for db file i/o
"""

import io
from typing import *

from .block import Block
from .block_storage import BlockStorage
from .metadata import Metadata
from .table import Table


class DBFile(BlockStorage):
    def __init__(self, filename) -> None:
        self.filename = filename
        self.file = open(filename, "r+b", 2 ** 23)
        self.file.write(b'\0' * 4096 * 17)

    def get_metadata(self) -> 'Metadata':
        return Metadata(self)

    def get_tables(self) -> List[Table]:
        return [Table(self, i) for i in range(0, 16)]

    def read_block(self, block_num) -> Block:
        self.file.seek(4096 * block_num)
        try:
            data = Block(self.file.read(4096))
        except AssertionError:
            raise AssertionError("Block " + str(block_num) + " does not exist")
        return data

    def write_block(self, block_num: int, block: Block) -> None:
        self.file.seek(4096 * block_num)
        self.file.write(block.data)

    def allocate_block(self) -> int:
        self.file.seek(0, io.SEEK_END)
        self.file.write(b'\0' * 4096)
        c = self.get_metadata().get_data_blocks_count()
        self.get_metadata().set_data_blocks_count(c + 1)
        return c + 17

    def close(self) -> None:
        self.file.flush()
        self.file.close()

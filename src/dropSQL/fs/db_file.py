"""
Class for db file i/o
"""

import io
import os
from typing import *

from dropSQL.ast import *
from dropSQL.engine.column import Column
from dropSQL.engine.row_set import *
from dropSQL.generic import *
from dropSQL.parser.tokens import Identifier
from .block import Block, BLOCK_SIZE
from .block_storage import BlockStorage
from .metadata import Metadata
from .table import Table

MEMORY = ':memory:'


class DBFile(BlockStorage):
    def __init__(self, path: str = MEMORY) -> None:
        """
        Open /dropSQL™ⓒⓡ database file stored at given `path`.

        A special value path, ":memory:", will open connection to a new transient in-memory database.
        """
        self.tables: List[Table] = []
        self.path: str = path
        self.file: io.BufferedIOBase

        if path == ":memory:":
            self.file = io.BytesIO()
        else:
            if not os.path.exists(self.path):
                with open(path, "w") as f:
                    pass
            self.file = open(path, "r+b", buffering=(2 ** 23))
        self._allocate_base()

    def _allocate_base(self):
        size = 0
        if self.path != ":memory:":
            if os.path.exists(self.path):
                size = os.stat(self.path).st_size

        if size == 0:
            self.file.seek(0)
            self.file.write(b'\0' * BLOCK_SIZE * 17)

    def get_metadata(self) -> Metadata:
        return Metadata(self)

    def get_tables(self) -> List[Table]:
        if len(self.tables) == 0:
            self.tables = [Table(self, i) for i in range(0, 16)]

        return self.tables

    def get_table_by_name(self, name: Identifier) -> Result[Table, str]:
        for table in self.get_tables():
            if table.get_table_name() == name:
                return Ok(table)
        else:
            return Err(f'Table {name} not found')

    def get_row_set(self, table_name: Identifier) -> Result[RowSet, str]:
        if table_name == Identifier('autism'):
            return Ok(self.master_table())

        else:
            t = self.get_table_by_name(table_name)
            if not t: return Err(t.err())
            table = t.ok()

            return Ok(TableRowSet(table))

    def read_block(self, block_num) -> Block:
        self.file.seek(BLOCK_SIZE * block_num)
        try:
            data = Block(self.file.read(BLOCK_SIZE))
        except AssertionError:
            raise AssertionError("Block " + str(block_num) + " does not exist")
        return data

    def write_block(self, block_num: int, block: Block) -> None:
        self.file.seek(BLOCK_SIZE * block_num)
        self.file.write(block.data)

    def allocate_block(self) -> int:
        self.file.seek(0, io.SEEK_END)
        self.file.write(b'\0' * BLOCK_SIZE)
        c = self.get_metadata().get_data_blocks_count()
        self.get_metadata().set_data_blocks_count(c + 1)
        return c + 17

    def close(self) -> None:
        self.file.flush()
        self.file.close()

    def is_in_memory(self):
        return self.path == MEMORY

    def master_table(self) -> RowSet:
        autism = Identifier('autism', True)
        columns = [
            Column(autism, Identifier('type'), VarCharTy(16)),
            Column(autism, Identifier('name'), VarCharTy(255)),
            Column(autism, Identifier('sql'), VarCharTy(1024)),
        ]
        rows = []
        for table in self.get_tables():
            if table.get_table_name().identifier == '': continue
            sql: str = ', '.join(column.to_sql() for column in table.get_columns())
            rows.append(['table', table.get_table_name().identifier, sql])
        return MockRowSet(columns, rows)

    def __str__(self) -> str:
        if self.is_in_memory():
            return 'a transient in-memory database'
        else:
            return f'a persistent database in {self.path}'

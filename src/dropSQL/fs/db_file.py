"""
Class for db file i/o
"""

import io
import os
from typing import *

from dropSQL.ast import *
from dropSQL.engine.column import Column
from dropSQL.engine.row_set import *
from dropSQL.engine.types import *
from dropSQL.generic import *
from dropSQL.parser.tokens import Identifier
from .block import Block, BLOCK_SIZE
from .block_storage import BlockStorage
from .metadata import Metadata
from .table import Table


def open_db(path: str) -> io.BufferedIOBase:
    if path == MEMORY:
        return io.BytesIO()
    else:
        if not os.path.exists(path):
            # touch file
            with open(path, "w"): pass
        return open(path, "r+b", buffering=16 * BLOCK_SIZE)


class DBFile(BlockStorage):
    def __init__(self, path: str = MEMORY) -> None:
        """
        Open /dropSQL™ⓒⓡ database file stored at given `path`.

        A special value path, ":memory:", will open connection to a new transient in-memory database.
        """
        self.tables: List[Table] = []
        self.path: str = path
        self.file: io.BufferedIOBase = open_db(self.path)
        self.blocks = self.storage_size() // BLOCK_SIZE

        self._init_base()

    def storage_size(self) -> int:
        if isinstance(self.file, io.BytesIO):
            return len(self.file.getbuffer())
        else:
            return os.stat(self.file.fileno()).st_size

    def _init_base(self) -> None:
        size = self.storage_size()

        if size % BLOCK_SIZE != 0:
            raise ValueError(f'Database size is not a multiple of {BLOCK_SIZE}')

        if size == 0:
            for i in range(17):
                self.allocate_block()

    def _maybe_update_metadata_block_count(self) -> None:
        if self.blocks >= 17:
            self.metadata.data_blocks_count = self.blocks - 17

    @property
    def metadata(self) -> Metadata:
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

    def new_table(self) -> Result[Table, str]:
        for table in self.get_tables():
            if table.get_table_name().identifier == '':
                return Ok(table)
        else:
            return Err('Can not allocate any more tables')

    def get_row_set(self, table_name: Identifier) -> Result[RowSet, str]:
        if table_name == Identifier('autism'):
            return Ok(self.master_table())

        else:
            t = self.get_table_by_name(table_name)
            if not t: return Err(t.err())
            table = t.ok()

            return Ok(TableRowSet(table))

    ################
    # BlockStorage #
    ################

    def read_block(self, index: int) -> Block:
        assert index < self.blocks, f'Block {index} does not exist'

        self.file.seek(index * BLOCK_SIZE)
        block = Block(self.file.read(BLOCK_SIZE), index)
        return block

    def write_block(self, block: Block) -> None:
        assert block.idx < self.blocks, f'Block {block.idx} does not exist'

        self.file.seek(block.idx * BLOCK_SIZE)
        self.file.write(block)

    def allocate_block(self) -> Block:
        block = Block.empty(self.blocks)
        self.blocks += 1
        self._maybe_update_metadata_block_count()
        self.write_block(block)
        return block

    def count_blocks(self) -> int:
        return self.blocks

    #################
    # Miscellaneous #
    #################

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
        rows: List[List[str]] = []
        for table in self.get_tables():
            name = table.get_table_name()
            if name.identifier == '': continue
            sql = CreateTable(None, name, table.get_columns()).to_sql()
            rows.append(['table', name.identifier, sql])
        return MockRowSet(columns, rows)

    def __str__(self) -> str:
        if self.is_in_memory():
            return 'a transient in-memory database'
        else:
            return f'a persistent database in {self.path}'

from dropSQL.engine.types import *
from .block import *
from .block_storage import BlockStorage

NAME_LENGTH = 256


class Metadata:
    def __init__(self, connection: BlockStorage):
        self.connection = connection
        self.block: Block = connection.read_block(0)

    @property
    def name(self) -> str:
        return (self.block[:NAME_LENGTH].partition(b'\0'))[0].decode("UTF-8")

    @name.setter
    def name(self, name: str) -> None:
        encoded = name.encode("UTF-8")
        assert len(encoded) < NAME_LENGTH - 1, 'Database name is too long'  # -1 for zero byte

        self.block[:NAME_LENGTH] = encoded.ljust(NAME_LENGTH, b'\0')
        self.connection.write_block(self.block)

    @property
    def data_blocks_count(self) -> int:
        """ Number of data blocks, excluding DB meta block and table meta blocks. """
        block = self.connection.read_block(0)
        count = block[NAME_LENGTH:NAME_LENGTH + POINTER_SIZE]
        return int.from_bytes(count, byteorder=BYTEORDER)

    @data_blocks_count.setter
    def data_blocks_count(self, count: int) -> None:
        count = count.to_bytes(POINTER_SIZE, byteorder=BYTEORDER)
        self.block[NAME_LENGTH:NAME_LENGTH + POINTER_SIZE] = count
        self.connection.write_block(self.block)

    @property
    def blocks_count(self) -> int:
        """ Total number of blocks, including meta blocks. """
        return 17 + self.data_blocks_count

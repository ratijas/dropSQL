from dropSQL.engine.types import *

__all__ = [
    'Block',
    'BLOCK_SIZE',
    'DIRECT_POINTERS',
    'POINTER_SIZE',
    'POINTERS_PER_BLOCK',
]


class Block(bytearray):
    """
    Block is the unit of physical stored information in the database
    """

    def __init__(self, data: bytes, index: int = 0):
        """
        Create new block object from initial bytes of data and index.

        :param data: Initial bytes, must have the size equal to BLOCK_SIZE.
        :param index: Physical index of block in the storage.
        """
        assert len(data) == BLOCK_SIZE, 'Incorrect block size: {}'.format(len(data))
        super().__init__(data)

        self.idx = index

    @classmethod
    def empty(cls, index: int = 0) -> 'Block':
        """
        Create empty block filled with zeroes.

        :param index: Physical index of block in the storage.
        :return: New block object.
        """
        return Block(_ZEROES, index)

    def override(self, offset: int, data: bytes) -> None:
        assert offset + len(data) <= BLOCK_SIZE

        self[offset:offset + len(data)] = data

    def get_pointer(self, index: int) -> int:
        assert 0 <= index < POINTERS_PER_BLOCK

        binary = self[index * POINTER_SIZE:(index + 1) * POINTER_SIZE]
        pointer = int.from_bytes(binary, byteorder=BYTEORDER)

        return pointer

    def set_pointer(self, index: int, pointer: int) -> None:
        assert 0 <= index < POINTERS_PER_BLOCK

        binary = pointer.to_bytes(POINTER_SIZE, byteorder=BYTEORDER)
        self.override(index * POINTER_SIZE, binary)


BLOCK_SIZE = 12 * 1024  # you know, for 12k...
_ZEROES = b'\0' * BLOCK_SIZE
POINTER_SIZE = 4
POINTERS_PER_BLOCK = BLOCK_SIZE // POINTER_SIZE
DIRECT_POINTERS = 10

import abc

from .block import Block


class BlockStorage(metaclass=abc.ABCMeta):
    """
    Physical block storage interface.
    """

    @abc.abstractmethod
    def read_block(self, index: int) -> Block:
        """
        Read physical block at index `index` from the storage.

        :param index: Block index starting from 0.
        :return: Block object.
        :raise AssertionError: If block does not exist.
        """

    @abc.abstractmethod
    def write_block(self, block: Block) -> None:
        """
        Write physical block at index `index` into the storage, replacing old data in-place.

        :param block: Block object.
        :raise AssertionError: If block does not exist.
        """

    @abc.abstractmethod
    def allocate_block(self) -> Block:
        """
        Allocate new physical block at the end of the storage.

        :return: New block object.
        """

    @abc.abstractmethod
    def count_blocks(self) -> int:
        """
        Return total number of physical blocks present in the storage.

        :return: Non-negative number of blocks.
        """

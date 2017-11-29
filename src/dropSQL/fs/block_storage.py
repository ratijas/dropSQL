import abc

from .block import Block


class BlockStorage(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def read_block(self, block_num) -> Block:
        ...

    @abc.abstractmethod
    def write_block(self, block_num: int, block: Block) -> None:
        ...

    @abc.abstractmethod
    def allocate_block(self) -> int:
        ...

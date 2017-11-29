from .block import Block, BLOCK_SIZE
from .block_storage import BlockStorage


class Metadata:
    def __init__(self, connection: BlockStorage):
        self.connection = connection

    def get_name(self) -> str:
        return (self.connection.read_block(0).data[0:256].split(b'\0'))[0].decode("UTF-8")

    def set_name(self, name: str) -> None:
        encoded = name.encode("UTF-8")
        assert len(encoded) < 255, "Database name is too long"
        try:
            block = self.connection.read_block(0)
        except AssertionError:
            block = Block(b'\0' * BLOCK_SIZE)
        block.data = encoded + block.data[len(encoded):BLOCK_SIZE]
        self.connection.write_block(0, block)

    def get_data_blocks_count(self) -> int:
        return int.from_bytes(self.connection.read_block(0).data[255:259], byteorder='big')

    def set_data_blocks_count(self, count: int) -> None:
        data = self.connection.read_block(0).data
        data = data[0:255] + count.to_bytes(4, byteorder='big') + data[259:]
        self.connection.write_block(0, Block(data))

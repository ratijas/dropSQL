from dropSQL.fs.db_file import DBFile


class Metadata:
    def __init__(self, connection: DBFile):
        self.connection = connection

    def get_name(self):
        return (self.connection.read_block(0).data[0:256].split(b'\0'))[0].decode("UTF-8")

    def set_name(self, name: str):
        encoded = name.encode("UTF-8")
        assert len(encoded) < 255, "Database name is too long"
        try:
            block = self.connection.read_block(0)
        except AssertionError:
            from dropSQL.fs.block import Block
            block = Block(b'\0' * 4096)
        block.data = encoded + block.data[len(encoded):4096]
        self.connection.write_block(0, block)

    def get_data_blocks_count(self):
        return int.from_bytes(self.connection.read_block(0).data[255:259], byteorder='big')

    def set_data_blocks_count(self, count: int):
        from dropSQL.fs.block import Block
        data = self.connection.read_block(0).data
        data = data[0:255] + count.to_bytes(4, byteorder='big') + data[259:]
        self.connection.write_block(0, Block(data))


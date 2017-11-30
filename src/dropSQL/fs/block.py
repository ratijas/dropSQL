class Block:
    def __init__(self, data: bytes):
        assert len(data) == BLOCK_SIZE, "Incorrect block size: {}".format(len(data))
        self.data = data


BLOCK_SIZE = 4096
POINTER_SIZE = 4

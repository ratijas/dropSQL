class Block:
    def __init__(self, data: bytes):
        assert len(data) == 4096, "Incorrect block size: {}".format(len(data))
        self.data = data

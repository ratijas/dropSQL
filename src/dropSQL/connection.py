MEMORY = ':memory:'


class Connection:
    def __init__(self, path=MEMORY) -> None:
        self.path = path

    def close(self):
        pass

    def is_in_memory(self):
        return self.path == MEMORY

    def __str__(self) -> str:
        if self.is_in_memory():
            return 'a transient in-memory database'
        else:
            return f'a persistent database in {self.path}'

    def execute(self, query):
        pass

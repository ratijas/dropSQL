from . import *


class Placeholder(Token):
    def __init__(self, index: int) -> None:
        super().__init__()

        self.index = index

    def __eq__(self, o: 'Placeholder') -> bool:
        return isinstance(o, Placeholder) and self.index == o.index

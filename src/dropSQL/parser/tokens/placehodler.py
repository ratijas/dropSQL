from .token import Token


class Placeholder(Token):
    def __init__(self, index: int) -> None:
        super().__init__()

        self.index = index

    def __repr__(self) -> str:
        return f'Token(?{str(self.index)})'

    def __eq__(self, o: object) -> bool:
        return isinstance(o, Placeholder) and self.index == o.index

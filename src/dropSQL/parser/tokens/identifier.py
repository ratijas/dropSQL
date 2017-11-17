from . import *


class Identifier(Token):
    def __init__(self, identifier: str, slash: bool = False) -> None:
        super().__init__()

        self.identifier = identifier
        self.slash = slash

    def __str__(self) -> str:
        if self.slash:
            return f'/{self.identifier}'
        else:
            return f'{self.identifier}'

    def __eq__(self, o: 'Identifier') -> bool:
        return isinstance(o, Identifier) and self.identifier.lower() == o.identifier.lower()

import abc

from . import *

__all__ = (
    'IdentifierBase',
    'Identifier',
    'Reserved',
)


class IdentifierBase(Token, metaclass=abc.ABCMeta):
    """
    Abstract base class for identifiers and reserved keywords.
    """

    def __init__(self, identifier: str, slash: bool = False) -> None:
        super().__init__()

        self.identifier = identifier
        self.slash = slash

    def __str__(self) -> str:
        if self.slash:
            return f'/{self.identifier}'
        else:
            return f'{self.identifier}'

    def __repr__(self):
        return str(self)

    def __eq__(self, o: 'IdentifierBase') -> bool:
        return isinstance(o, self.__class__) and self.identifier.lower() == o.identifier.lower()

    def __hash__(self) -> int:
        return self.identifier.lower().__hash__()


class Identifier(IdentifierBase):
    def __repr__(self) -> str:
        return f'Identifier( {super().__repr__()} )'


class Reserved(IdentifierBase):
    def __repr__(self) -> str:
        return f'Reserved( {super().__repr__()} )'

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

    def __eq__(self, o: 'IdentifierBase') -> bool:
        return isinstance(o, self.__class__) and self.identifier.lower() == o.identifier.lower()


class Identifier(IdentifierBase):
    pass


class Reserved(IdentifierBase):
    pass

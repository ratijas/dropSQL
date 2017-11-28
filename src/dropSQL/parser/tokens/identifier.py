import abc

from .token import Token

__all__ = [
    'IdentifierBase',
    'Identifier',
    'Keyword',
]


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

    def __eq__(self, o: object) -> bool:
        return isinstance(o, type(self)) and self.identifier.lower() == o.identifier.lower()


class Identifier(IdentifierBase):
    def __repr__(self) -> str:
        return f'Identifier({super().__repr__()})'

    def maybe_as_keyword(self) -> Token:
        from .ident_to_keyword import KEYWORDS
        keyword = KEYWORDS.get(self.identifier.lower(), None)
        if keyword is not None:
            return keyword

        else:
            return self


class Keyword(IdentifierBase):
    def __repr__(self) -> str:
        return f'Keyword({super().__repr__()})'

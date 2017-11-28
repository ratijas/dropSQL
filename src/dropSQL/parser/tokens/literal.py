import abc
from typing import *

from .token import Token

__all__ = [
    'Literal',
    'Integer',
    'Float',
    'VarChar',
]

T = TypeVar('T', int, float, str)


class Literal(Token, Generic[T], metaclass=abc.ABCMeta):
    def __init__(self, value: T) -> None:
        super().__init__()

        self.value: T = value

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.value!r})'

    def __eq__(self, o: object) -> bool:
        return isinstance(o, type(self)) and self.value == o.value


class Integer(Literal[int]): pass


class Float(Literal[float]): pass


class VarChar(Literal[str]): pass

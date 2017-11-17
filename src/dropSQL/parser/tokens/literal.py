from typing import *
from . import *

__all__ = (
    'Literal',
    'Integer',
    'Float',
    'String',
)

T = TypeVar('T', int, float, str)


class Literal(Token, Generic[T]):
    def __init__(self, value: T) -> None:
        super().__init__()

        self.value: T = value

    def __eq__(self, o: T) -> bool:
        return isinstance(o, type(self)) and self.value == o.value


class Integer(Literal[int]): pass


class Float(Literal[float]): pass


class String(Literal[str]): pass

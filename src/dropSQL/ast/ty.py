import abc

from .ast import Ast

__all__ = [
    'Ty',
    'IntegerTy',
    'FloatTy',
    'VarCharTy',
]


class Ty(Ast, metaclass=abc.ABCMeta): pass


class IntegerTy(Ty):
    def to_sql(self) -> str:
        return 'integer'


class FloatTy(Ty):
    def to_sql(self) -> str:
        return 'float'


class VarCharTy(Ty):
    def __init__(self, width: int) -> None:
        super().__init__()

        self.width = width

    def to_sql(self) -> str:
        return f'varchar({self.width})'

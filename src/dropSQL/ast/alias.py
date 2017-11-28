import abc
from typing import *

from . import *


class Alias(Ast, metaclass=abc.ABCMeta):
    def __init__(self, alias: Optional[Identifier] = None) -> None:
        super().__init__()

        self.alias = alias

    def to_sql(self) -> str:
        if self.alias is None:
            return ''
        else:
            return f' /as {str(self.alias)}'


class AliasedTable(Alias):
    def __init__(self, name: Identifier, alias: Optional[Identifier] = None) -> None:
        super().__init__(alias)

        self.name = name

    def to_sql(self) -> str:
        s = str(self.name)
        s += super().to_sql()
        return s


class AliasedExpression(Alias):
    def __init__(self, expression: Expression, alias: Optional[Identifier] = None) -> None:
        super().__init__(alias)

        self.expression = expression

    def to_sql(self) -> str:
        expr = self.expression.to_sql()
        expr += super().to_sql()
        return expr

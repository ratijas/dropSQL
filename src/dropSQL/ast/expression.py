import abc
from typing import *

from parser.tokens import Operator
from . import *

__all__ = (
    'Expression',
    'ExpressionLiteral',
    'ExpressionLiteralInt',
    'ExpressionLiteralFloat',
    'ExpressionLiteralString',
    'ExpressionPlaceholder',
    'ExpressionReference',
    'ExpressionParen',
    'ExpressionBinary',
)


class Expression(Ast, metaclass=abc.ABCMeta): pass


T = TypeVar('T', int, float, str)


class ExpressionLiteral(Expression, Generic[T]):
    def __init__(self, lit: T) -> None:
        super().__init__()

        self.value = lit


class ExpressionLiteralInt(ExpressionLiteral[int]):
    def __init__(self, lit: int) -> None:
        super().__init__(lit)

    def to_sql(self) -> str:
        return f'{self.value}'


class ExpressionLiteralFloat(ExpressionLiteral[float]):
    def __init__(self, lit: float) -> None:
        super().__init__(lit)

    def to_sql(self) -> str:
        return '%f' % self.value


class ExpressionLiteralString(ExpressionLiteral[str]):
    def __init__(self, lit: str) -> None:
        super().__init__(lit)

    def to_sql(self) -> str:
        s = '\''
        value = self.value
        value = value.replace('\\', '\\\\')  # first escape the 'escape' symbol
        value = value.replace('\'', '\\\'')  # then escape the quote
        s += value
        s += '\''
        return s


class ExpressionPlaceholder(Expression):
    def __init__(self, index: int) -> None:
        super().__init__()

        self.index = index

    def to_sql(self) -> str:
        return f'?{self.index}'


class ExpressionReference(Expression):
    """ Reference to a /table/column """

    def __init__(self, table: Optional[Identifier], column: Identifier) -> None:
        super().__init__()

        if table is not None:
            table = Identifier(table.identifier, True)
        self.table = table
        self.column = Identifier(column.identifier, True)

    def to_sql(self) -> str:
        s = ''
        if self.table is not None:
            s += str(self.table)
        s += str(self.column)
        return s


class ExpressionParen(Expression):
    def __init__(self, inner: Expression) -> None:
        super().__init__()

        self.inner = inner

    def to_sql(self) -> str:
        s = '('
        s += self.inner.to_sql()
        s += ')'
        return s


class ExpressionBinary(Expression):
    def __init__(self, operator: Operator, lhs: Expression, rhs: Expression) -> None:
        super().__init__()

        self.operator = operator
        self.lhs = lhs
        self.rhs = rhs

    def to_sql(self) -> str:
        s = ''
        s += self.lhs.to_sql()
        s += ' '
        s += self.operator.operator
        s += ' '
        s += self.rhs.to_sql()
        return s

import abc
from typing import *

from dropSQL.generic import *
from dropSQL.parser.streams import *
from dropSQL.parser.tokens import *
from .ast import Ast, FromSQL

__all__ = [
    'Expression',
    'ExpressionLiteral',
    'ExpressionLiteralInt',
    'ExpressionLiteralFloat',
    'ExpressionLiteralVarChar',
    'ExpressionPlaceholder',
    'ExpressionReference',
    'ExpressionParen',
    'ExpressionBinary',
]


class Expression(Ast, FromSQL['Expression'], metaclass=abc.ABCMeta):
    @classmethod
    def from_sql(cls, tokens: Stream[Token]) -> IResult['Expression']:
        """
        expr
            : expr binary_operator expr
            | literal
            | placeholder
            | /table_name /column_name
            |             /column_name
            | "(" expr ")"
            ;
        """
        res = cls.parse_no_binary(tokens)
        if not res: return IErr(res.err())
        lhs = res.ok()

        # try binary operator
        t = tokens.peek().and_then(Cast(Operator))
        if not t: return IOk(lhs)
        op = t.ok()
        tokens.next()

        res = cls.from_sql(tokens)
        if not res: return IErr(res.err().empty_to_incomplete())
        rhs = res.ok()

        return IOk(ExpressionBinary(op, lhs, rhs))

    @classmethod
    def parse_no_binary(cls, tokens: Stream[Token]) -> IResult['Expression']:
        t = tokens.next()
        if not t: return IErr(t.err().empty_to_incomplete())

        tok = t.ok()
        if isinstance(tok, Integer):
            return IOk(ExpressionLiteralInt(tok.value))

        if isinstance(tok, Float):
            return IOk(ExpressionLiteralFloat(tok.value))

        if isinstance(tok, VarChar):
            return IOk(ExpressionLiteralVarChar(tok.value))

        if isinstance(tok, Placeholder):
            return IOk(ExpressionPlaceholder(tok.index))

        if isinstance(tok, Identifier):
            t = tokens.peek().and_then(Cast(Identifier))
            if t:
                tokens.next()
                return IOk(ExpressionReference(tok, t.ok()))

            else:
                return IOk(ExpressionReference(None, tok))

        if isinstance(tok, LParen):
            expr = cls.from_sql(tokens)
            if not expr: return IErr(expr.err().empty_to_incomplete())

            t = tokens.next().and_then(Cast(RParen))
            if not t: return IErr(t.err().empty_to_incomplete())

            return IOk(ExpressionParen(expr.ok()))

        return Err(Syntax('expression', str(tok)))


T = TypeVar('T', int, float, str)


class ExpressionLiteral(Expression, Generic[T]):
    def __init__(self, lit: T) -> None:
        super().__init__()

        self.value: T = lit

    def __eq__(self, o: object) -> bool:
        return isinstance(o, type(self)) and self.value == o.value


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


class ExpressionLiteralVarChar(ExpressionLiteral[str]):
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

        self.table = table
        self.column = column

    def to_sql(self) -> str:
        s = ''
        if self.table is not None:
            s += str(self.table)
            if not self.column.slash:
                s += ' '
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

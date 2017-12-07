import abc
from typing import *

from dropSQL.generic import *
from dropSQL.parser.streams import *
from dropSQL.parser.tokens import *
from .ast import Ast, FromSQL

if TYPE_CHECKING:
    from dropSQL.engine.types import *
    from dropSQL.engine.context import Context

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
    'PrimitiveTy',
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

    @abc.abstractmethod
    def eval_with(self, context: 'Context') -> Result['DB_TYPE', str]:
        """
        Evaluate expression within given database context.
        :return: Positive result with scalar value, or error description.
        """


PrimitiveTy = TypeVar('PrimitiveTy', int, float, str)


class ExpressionLiteral(Expression, Generic[PrimitiveTy]):
    def __init__(self, lit: PrimitiveTy) -> None:
        super().__init__()

        self.value: PrimitiveTy = lit

    def __eq__(self, o: object) -> bool:
        return isinstance(o, type(self)) and self.value == o.value


class ExpressionLiteralInt(ExpressionLiteral[int]):
    def __init__(self, lit: int) -> None:
        assert isinstance(lit, int)
        super().__init__(lit)

    def to_sql(self) -> str:
        return f'{self.value}'

    def eval_with(self, _: 'Context') -> Result[int, str]:
        return Ok(self.value)


class ExpressionLiteralFloat(ExpressionLiteral[float]):
    def __init__(self, lit: float) -> None:
        assert isinstance(lit, float)
        super().__init__(lit)

    def to_sql(self) -> str:
        return '%f' % self.value

    def eval_with(self, _: 'Context') -> Result[float, str]:
        return Ok(self.value)


class ExpressionLiteralVarChar(ExpressionLiteral[str]):
    def __init__(self, lit: str) -> None:
        assert isinstance(lit, str)
        super().__init__(lit)

    def to_sql(self) -> str:
        s = '\''
        value = self.value
        value = value.replace('\\', '\\\\')  # first escape the 'escape' symbol
        value = value.replace('\'', '\\\'')  # then escape the quote
        value = value.replace('\n', '\\n')  # and new line
        s += value
        s += '\''
        return s

    def eval_with(self, _: 'Context') -> Result[str, str]:
        return Ok(self.value)


class ExpressionPlaceholder(Expression):
    """
    Placeholder uses 1-based indexes for arguments.
    """

    def __init__(self, index: int) -> None:
        super().__init__()
        assert index > 0

        self.index = index

    def to_sql(self) -> str:
        return f'?{self.index}'

    def eval_with(self, context: 'Context') -> Result['DB_TYPE', str]:
        if len(context.args) <= (self.index - 1): return Err(f'Not enough arguments')
        lit: DB_TYPE = context.args[self.index - 1]
        return Ok(lit)


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

    def eval_with(self, context: 'Context') -> Result['DB_TYPE', str]:
        # TODO: cache index
        # find column with corresponding table and column names
        for i, column in enumerate(context.row.set.columns()):
            if self.table is None:
                if self.column == column.name:
                    return Ok(context.row.data[i])
            else:
                if self.table == column.table and self.column == column.name:
                    return Ok(context.row.data[i])

        return Err(f'Reference not found in context: {self.to_sql()}')


class ExpressionParen(Expression):
    def __init__(self, inner: Expression) -> None:
        super().__init__()

        self.inner = inner

    def to_sql(self) -> str:
        s = '('
        s += self.inner.to_sql()
        s += ')'
        return s

    def eval_with(self, context: 'Context') -> Result['DB_TYPE', str]:
        return self.inner.eval_with(context)


class ExpressionBinary(Expression):
    def __init__(self, op: Operator, lhs: Expression, rhs: Expression) -> None:
        super().__init__()

        self.operator = op
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

    def eval_with(self, context: 'Context') -> Result['DB_TYPE', str]:
        lhs = self.lhs.eval_with(context)
        if not lhs: return Err(lhs.err())
        lhs = lhs.ok()

        rhs = self.rhs.eval_with(context)
        if not rhs: return Err(rhs.err())
        rhs = rhs.ok()

        op = self.operator.operator
        try:
            if op == Operator.EQ:
                return Ok(int(lhs == rhs))

            elif op == Operator.NE:
                return Ok(int(lhs != rhs))

            elif op == Operator.ADD:
                return Ok(lhs + rhs)

            elif op == Operator.SUB:
                return Ok(lhs - rhs)

            elif op == Operator.MUL:
                return Ok(lhs * rhs)

            elif op == Operator.DIV:
                try:
                    return Ok(lhs / rhs)

                except ZeroDivisionError as e:
                    return Err(str(e))

            elif op == Operator.GT:
                return Ok(int(lhs > rhs))

            elif op == Operator.LT:
                return Ok(int(lhs < rhs))

            elif op == Operator.GE:
                return Ok(int(lhs >= rhs))

            elif op == Operator.LE:
                return Ok(int(lhs <= rhs))

            elif op == Operator.AND:
                return Ok(int(bool(lhs) and bool(rhs)))

            elif op == Operator.OR:
                return Ok(int(bool(lhs) or bool(rhs)))

            else:
                return Err(f'Unsupported operator: {op}')

        except TypeError as e:
            return Err(str(e))

import abc

from dropSQL.generic import *
from dropSQL.parser.streams import *
from dropSQL.parser.tokens import *
from .alias import AliasedExpression
from .ast import Ast, FromSQL

__all__ = [
    'ResultColumn',
    'ResultStar',
    'ResultExpression',
]


class ResultColumn(Ast, FromSQL['ResultColumn'], metaclass=abc.ABCMeta):
    """
    Abstract base class for "/select col1, col2 + 1 /as banana, *".

    - aliased expression
    - star
    """

    @classmethod
    def from_sql(cls, tokens: Stream[Token]) -> IResult['ResultColumn']:
        """
        /result_column
            : "*"
            | /aliased_expression
            ;
        """
        t = tokens.peek().and_then(Cast(Operator))
        if t:
            if t.ok().operator != Operator.MUL: return IErr(Syntax('STAR or expression', str(t.ok())))
            tokens.next().ok()
            return IOk(ResultStar())

        t = AliasedExpression.from_sql(tokens)
        if not t: return IErr(t.err())

        return IOk(ResultExpression(t.ok()))

    # for the sake of static typing
    def is_star(self) -> bool:
        raise NotImplementedError

    def as_star(self) -> 'ResultStar':
        raise NotImplementedError

    def is_expression(self) -> bool:
        raise NotImplementedError

    def as_expression(self) -> 'ResultExpression':
        raise NotImplementedError


class ResultStar(ResultColumn):
    def __init__(self) -> None:
        super().__init__()

    def to_sql(self) -> str:
        return '*'

    def is_star(self) -> bool:
        return True

    def is_expression(self) -> bool:
        return False

    def as_star(self) -> 'ResultStar':
        return self


class ResultExpression(ResultColumn):
    def __init__(self, expression: AliasedExpression) -> None:
        super().__init__()

        self.expression = expression

    def to_sql(self) -> str:
        return self.expression.to_sql()

    def is_star(self) -> bool:
        return False

    def is_expression(self) -> bool:
        return True

    def as_expression(self) -> 'ResultExpression':
        return self

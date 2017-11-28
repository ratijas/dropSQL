import abc

from .alias import AliasedExpression
from .ast import Ast


class ResultColumn(Ast, metaclass=abc.ABCMeta):
    """
    Abstract base class for "/select col1, col2 + 1, *".

    - aliased expression
    - star
    """


class ResultStar(ResultColumn):
    def __init__(self) -> None:
        super().__init__()

    def to_sql(self) -> str:
        return '*'


class ResultExpression(ResultColumn):
    def __init__(self, expression: AliasedExpression) -> None:
        super().__init__()

        self.expression = expression

    def to_sql(self) -> str:
        return self.expression.to_sql()

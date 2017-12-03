import abc
from typing import *

from dropSQL.generic import *
from dropSQL.parser.streams import *
from dropSQL.parser.tokens import *

__all__ = ['Ast', 'AstStmt', 'FromSQL']


class Ast(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def to_sql(self) -> str:
        """
        Like __str__, but explicitly states its purpose

        :return: Serialized statement.
        """

    def __repr__(self) -> str:
        return self.to_sql()


class AstStmt(Ast, metaclass=abc.ABCMeta):
    """
    Statement mix-in for Ast subclasses
    """

    @abc.abstractmethod
    def execute(self, db, args: List[Any] = ()) -> Result[None, None]:
        ...


class FromSQL(Generic[T]):
    """
    Parser mix-in.
    """

    @classmethod
    @abc.abstractmethod
    def from_sql(cls, tokens: Stream[Token]) -> IResult[T]:
        """
        Read /dropSQL tokens from `tokens` stream, and try to build up the result.
        Stream's next item is the first token we must work with.
        After returning `IOk`, stream must point to the last successfully processed token.
        """

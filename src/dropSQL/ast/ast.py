import abc
from typing import *

from dropSQL.generic import *


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

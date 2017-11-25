import abc
from typing import *

from . import *

__all__ = (
    'JoinAst',
    'CrossJoin',
    'InnerJoin',
)


class JoinAst(Ast, metaclass=abc.ABCMeta):
    def __init__(self, table: AliasedTable) -> None:
        super().__init__()

        self.table = table


class CrossJoin(JoinAst):
    def __init__(self, table: AliasedTable) -> None:
        super().__init__(table)

    def to_sql(self) -> str:
        join = ', '
        join += self.table.to_sql()

        return join


class InnerJoin(JoinAst):
    def __init__(self, table: AliasedTable, constraint: Optional[Expression] = None) -> None:
        super().__init__(table)

        self.constraint = constraint

    def to_sql(self) -> str:
        join = ' /join '
        join += self.table.to_sql()

        if self.constraint is not None:
            join += ' /on '
            join += self.constraint.to_sql()

        return join

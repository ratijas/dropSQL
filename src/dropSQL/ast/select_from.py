from typing import *

from dropSQL.parser.tokens import Comma, Join
from . import *


class InnerJoin(Ast):
    def __init__(self, style: Union[Comma, Join], table: AliasedTable, constraint: Optional[Expression] = None) -> None:
        super().__init__()

        self.style = style
        self.table = table
        self.constraint = constraint

    def to_sql(self) -> str:
        join = ''
        if isinstance(self.style, Comma):
            join += ', '
        elif isinstance(self.style, Join):
            join += str(self.style)
            join += ' '
        else:
            raise NotImplementedError

        join += self.table.to_sql()

        if self.constraint is not None:
            join += ' /on '
            join += self.constraint.to_sql()

        return join


class SelectFrom(Ast):
    """
    "/select" /result_columns
      "from" /from_body
      /where_clause
    """

    def __init__(self,
                 columns: List[ResultColumn],
                 table: AliasedTable,
                 joins: List[InnerJoin],
                 where: Optional[Expression]) -> None:
        super().__init__()

        self.columns = columns
        self.table = table
        self.joins = joins
        self.where = where

    def to_sql(self) -> str:
        stmt = '/select '

        stmt += ', '.join([column.to_sql() for column in self.columns])
        stmt += ' /from '
        stmt += self.table.to_sql()

        if len(self.joins) != 0:
            stmt += ' '
            stmt += ''.join([join.to_sql() for join in self.joins])

        if self.where is not None:
            stmt += ' /where '
            stmt += self.where.to_sql()

        return stmt

from typing import *

from .alias import AliasedTable
from .ast import AstStmt
from .expression import Expression
from .join import JoinAst
from .result_column import ResultColumn


class SelectFrom(AstStmt):
    """
    "/select" /result_columns
      "from" /from_body
      /where_clause
    """

    def __init__(self,
                 columns: List[ResultColumn],
                 table: AliasedTable,
                 joins: List[JoinAst] = list(),
                 where: Optional[Expression] = None) -> None:
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
            stmt += ''.join([join.to_sql() for join in self.joins])

        if self.where is not None:
            stmt += ' /where '
            stmt += self.where.to_sql()

        stmt += ' /drop'

        return stmt

from typing import *

from . import *


class UpdateSet(Ast, AstStmt):
    def __init__(self,
                 table: Identifier,
                 assign: List[Tuple[Identifier, Expression]],
                 where: Optional[Expression]) -> None:
        super().__init__()

        self.table = table
        self.assign = assign
        self.where = where

    def to_sql(self) -> str:
        stmt = '/update '
        stmt += str(self.table)
        stmt += ' /set '

        assignments = []
        for column, value in self.assign:
            buf = ''
            buf += str(column)
            buf += ' = '
            buf += value.to_sql()
            assignments.append(buf)
        stmt += ', '.join(assignments)

        if self.where is not None:
            stmt += ' /where '
            stmt += self.where.to_sql()

        stmt += ' /drop'
        return stmt

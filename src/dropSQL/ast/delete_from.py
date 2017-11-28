from typing import *

from .ast import AstStmt
from .expression import Expression
from .identifier import Identifier


class DeleteFrom(AstStmt):
    def __init__(self, table: Identifier, where: Optional[Expression]) -> None:
        super().__init__()

        self.table = table
        self.where = where

    def to_sql(self) -> str:
        stmt = '/delete from '
        stmt += str(self.table)

        if self.where is not None:
            stmt += ' /where '
            stmt += self.where.to_sql()

        stmt += ' /drop'
        return stmt
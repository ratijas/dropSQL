from typing import *

from .ast import AstStmt
from .existence import IfExists
from .identifier import Identifier


class DropTable(AstStmt):
    def __init__(self, if_exists: Optional[IfExists], table: Identifier) -> None:
        super().__init__()

        self.if_exists = if_exists
        self.table = table

    def to_sql(self) -> str:
        stmt = '/drop table '

        if self.if_exists is not None:
            stmt += self.if_exists.to_sql()
            stmt += ' '

        stmt += str(self.table)
        stmt += ' /drop'

        return stmt

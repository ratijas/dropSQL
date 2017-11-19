from typing import *

from . import *


class CreateTable(Ast):
    def __init__(self, if_not_exists: Optional[IfNotExists], name: Identifier, columns: List[ColumnDef]) -> None:
        super().__init__()

        self.if_not_exists: Optional[IfNotExists] = if_not_exists
        self.name: Identifier = name
        self.columns: List[ColumnDef] = columns

    def to_sql(self) -> str:
        stmt = '/create table '
        if self.if_not_exists is not None:
            stmt += self.if_not_exists.to_sql()
            stmt += ' '
        stmt += str(self.name)
        stmt += ' (\n'
        for col in self.columns:
            stmt += '\t'
            stmt += col.to_sql()
            stmt += '\n'
        stmt += ') /drop'

        return stmt

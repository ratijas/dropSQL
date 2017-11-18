from typing import *

from . import *
from ..parser.tokens import Identifier


class CreateTable(Ast):
    def __init__(self, if_not_exists: bool, table_name: Identifier, columns: List[ColumnDef]) -> None:
        super().__init__()

        self.if_not_exists: bool = if_not_exists
        self.table_name: Identifier = table_name
        self.columns: List[ColumnDef] = columns

    def to_sql(self) -> str:
        stmt = '/create table '
        if self.if_not_exists:
            stmt += 'if not exists '
        stmt += str(self.table_name)
        stmt += ' (\n'
        for col in self.columns:
            stmt += '\t'
            stmt += col.to_sql()
            stmt += ',\n'
        stmt += ') /drop'

        return stmt

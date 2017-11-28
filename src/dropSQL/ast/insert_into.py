from typing import *

from .ast import AstStmt
from .expression import Expression
from .identifier import Identifier


class InsertInto(AstStmt):
    def __init__(self, table: Identifier, columns: List[Identifier], values: List[List[Expression]]) -> None:
        super().__init__()

        self.table = table
        self.columns = columns
        self.values = values

    def to_sql(self) -> str:
        stmt = '/insert into '
        stmt += str(self.table)

        stmt += ' ('
        stmt += ', '.join(str(column) for column in self.columns)
        stmt += ') values '

        values: List[str] = []
        for value in self.values:
            buf = '('
            buf += ', '.join(expression.to_sql() for expression in value)
            buf += ')'
            values.append(buf)

        stmt += ', '.join(values)
        stmt += ' /drop'

        return stmt

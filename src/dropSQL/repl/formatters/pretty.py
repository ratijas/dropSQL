import os
from typing import *
from typing.io import TextIO

try:
    TextIO
except NameError:
    from typing.io import TextIO

from dropSQL.ast import ExpressionLiteral
from dropSQL.engine.row_set import *
from .formatter import Formatter

__all__ = ['PrettyFormatter']


class PrettyFormatter(Formatter):
    def __init__(self, row_set: RowSet) -> None:
        super().__init__()

        self.row_set = row_set
        self.separator = '  '

    @classmethod
    def with_row_set(cls, row_set: RowSet) -> 'Formatter':
        return PrettyFormatter(row_set)

    def format(self, f: TextIO) -> None:
        width: List[int] = []
        columns: List[str] = []
        rows: List[List[str]] = []

        for column in self.row_set.columns():
            name = str(column.name)
            columns.append(name)
            width.append(len(name))

        for row in self.row_set.iter():
            expressions: List[str] = []

            for (column, cell) in zip(self.row_set.columns(), row.data):
                expr: ExpressionLiteral = column.ty.construct(cell)
                sql = expr.to_sql()
                expressions.append(sql)

            rows.append(expressions)

        for row in rows:
            for (i, cell) in enumerate(row):
                width[i] = max(len(cell), width[i])

        f.write(' ')  # shift to the right for the sliding effect
        f.write(self.separator.join(c.center(w) for (c, w) in zip(columns, width)))
        f.write(os.linesep)
        f.write(self.separator.join(''.ljust(w, '/') for w in width))
        f.write(os.linesep)

        for row in rows:
            f.write(self.separator.join(c.ljust(w) for (c, w) in zip(row, width)))
            f.write(os.linesep)

import abc
from typing import *

from dropSQL.ast import Ty, Expression
from dropSQL.fs.table import Table
from dropSQL.parser.tokens import Identifier


class Row:
    def __init__(self, row_set: 'RowSet', data: List[Union[str, int, float]]):
        self.set = row_set
        self.data = data


class Column:
    def __init__(self, table: Identifier, name: Identifier, ty: Ty):
        self.table = table
        self.name = name
        self.ty = ty


class RowSet(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def columns(self) -> List[Column]:
        """
        Describe columns in this row set.
        """

    @abc.abstractmethod
    def iter(self) -> Iterator[Row]:
        """
        Return a generator which yields rows from the underlying row stream or a table.
        """

    @abc.abstractmethod
    def reset(self) -> None:
        """
        Reset iterator back to the first position.
        """


class TableRowSet(RowSet):
    def __init__(self, table: Table) -> None:
        self.table = table
        self.name = self.table.get_table_name()

    def columns(self) -> List[Column]:
        return [Column(self.name, column.name, column.ty)
                for column in self.table.get_columns()]

    def iter(self) -> Iterator[Row]:
        n = self.table.count_records()
        i = 0
        while i < n:
            try:
                row = self.table.select(i)
            except (RuntimeError, AttributeError) as _:
                i += 1
                continue
            i += 1

            yield row

    def reset(self) -> None:
        pass


class CrossJoinRowSet(RowSet):
    def __init__(self, lhs: RowSet, rhs: RowSet) -> None:
        self.lhs = lhs
        self.rhs = rhs

    def columns(self) -> List[Column]:
        return self.lhs.columns() + self.rhs.columns()

    def iter(self) -> Iterator[Row]:
        for left in self.lhs.iter():
            for right in self.rhs.iter():
                yield Row(self, left.data + right.data)
            self.rhs.reset()

    def reset(self) -> None:
        self.lhs.reset()
        self.rhs.reset()


class FilteredRowSet(RowSet):
    def __init__(self, inner: RowSet, expr: Expression) -> None:
        super().__init__()

        self.inner = inner
        self.expr = expr

    def columns(self) -> List[Column]:
        return self.inner.columns()

    def reset(self) -> None:
        return self.inner.reset()

    def iter(self) -> Iterator[Row]:
        for row in self.inner.iter():
            if self.expr.eval(row).to_integer() != 0:
                yield row


class LeftInnerJoin(RowSet):
    def __init__(self, lhs: RowSet, rhs: RowSet, on: Expression) -> None:
        self.inner = FilteredRowSet(CrossJoinRowSet(lhs, rhs), on)

    def columns(self) -> List[Column]:
        return self.inner.columns()

    def reset(self) -> None:
        return self.inner.reset()

    def iter(self) -> Iterator[Row]:
        yield from self.inner.iter()

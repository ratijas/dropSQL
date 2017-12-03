from typing import *

from ..row_set import RowSet
from ...column import Column
from ...row import Row


class CrossJoinRowSet(RowSet):
    """
    Cross Join produces all possible combinations from left and right tables' row sets.
    """

    def __init__(self, lhs: RowSet, rhs: RowSet) -> None:
        super().__init__()

        self.lhs = lhs
        self.rhs = rhs

    def columns(self) -> List[Column]:
        return self.lhs.columns() + self.rhs.columns()

    def iter(self) -> Iterator['Row']:
        for left in self.lhs.iter():
            for right in self.rhs.iter():
                yield Row(self, left.data + right.data)

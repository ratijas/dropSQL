from typing import *

from .cross import CrossJoinRowSet
from ..filtered import FilteredRowSet
from ..row_set import RowSet
from ...column import Column

if TYPE_CHECKING:
    from dropSQL.ast.expression import Expression
    from ...row import Row


class LeftInnerJoin(RowSet):
    def __init__(self, lhs: RowSet, rhs: RowSet, on: 'Expression') -> None:
        super().__init__()

        self.inner = FilteredRowSet(CrossJoinRowSet(lhs, rhs), on)

    def columns(self) -> List[Column]:
        return self.inner.columns()

    def iter(self) -> Iterator['Row']:
        yield from self.inner.iter()

from typing import *

from dropSQL.parser.tokens import Identifier
from .row_set import RowSet
from ..column import Column
from ..row import Row

if TYPE_CHECKING:
    pass


class RenameTableRowSet(RowSet):
    def __init__(self, inner: RowSet, rename: Identifier) -> None:
        super().__init__()

        self.inner = inner
        self._columns: List[Column] = [
            Column(rename, c.name, c.ty)
            for c in inner.columns()
        ]

    def columns(self) -> List[Column]:
        return self._columns

    def iter(self) -> Iterator[Row]:
        for row in self.inner.iter():
            new_row = Row(self, row.data, row.id)
            yield new_row

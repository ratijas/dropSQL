from typing import *

from .row_set import RowSet
from ..column import Column
from ..row import Row

if TYPE_CHECKING:
    from dropSQL import fs


class TableRowSet(RowSet):
    """
    Fetches row directly from the dropSQL table.
    """

    def __init__(self, table: 'fs.Table') -> None:
        super().__init__()

        self.table = table
        self.name = self.table.get_table_name()

    def columns(self) -> List[Column]:
        return [Column(self.name, column.name, column.ty)
                for column in self.table.get_columns()]

    def iter(self) -> Iterator[Row]:
        n = self.table.count_records()
        i = 0
        while i < n:
            res = self.table.select(i)
            if res:
                row = res.ok()
                yield Row(self, row, i)
            i += 1

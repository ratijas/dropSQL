from typing import *

from .row_set import RowSet
from ..column import Column
from ..row import Row
from ..types import *


class MockRowSet(RowSet):
    """ Mock row set for testing purposes. """

    def __init__(self, columns: List[Column], data: List[ROW_TYPE]) -> None:
        super().__init__()

        self._columns = columns
        self._data = data

    def columns(self) -> List[Column]:
        return self._columns

    def iter(self) -> Iterator[Row]:
        for (i, data) in enumerate(self._data):
            yield Row(self, data, i + 1)

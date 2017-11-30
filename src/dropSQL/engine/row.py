import collections.abc
from typing import *

from .row_set.empty import EmptyRowSet
from .types import *

if TYPE_CHECKING:
    from .row_set.row_set import RowSet


class Row(collections.abc.Sequence):
    def __init__(self, row_set: 'RowSet', data: ROW_TYPE):
        self.set = row_set
        self.data = data

    @classmethod
    def empty(cls) -> 'Row':
        return Row(EmptyRowSet(), [])

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return self.data.__getitem__(index)

    def __repr__(self) -> str:
        return 'Row({})'.format(', '.join(map(str, self.data)))

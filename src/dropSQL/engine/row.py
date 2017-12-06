import collections.abc
from typing import *

from .types import *

if TYPE_CHECKING:
    from .row_set import RowSet


class Row(collections.abc.Sequence):
    __slots__ = ['id', 'set', 'data']

    def __init__(self, row_set: 'RowSet', data: ROW_TYPE, ID: Optional[int] = None):
        self.id: Optional[int] = ID
        self.set = row_set
        self.data = data

    @classmethod
    def empty(cls) -> 'Row':
        from .row_set import EmptyRowSet
        return Row(EmptyRowSet(), [])

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return self.data.__getitem__(index)

    def __repr__(self) -> str:
        return 'Row({})'.format(', '.join(map(str, self.data)))

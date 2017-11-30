from typing import *

from .row_set import RowSet
from ..column import Column

if TYPE_CHECKING:
    from ..row import Row


class EmptyRowSet(RowSet):
    def columns(self) -> List[Column]:
        return []

    def iter(self) -> Iterator['Row']:
        yield from ()

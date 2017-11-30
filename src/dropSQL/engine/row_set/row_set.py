import abc
from typing import *

from ..column import Column

if TYPE_CHECKING:
    from ..row import Row


class RowSet(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def columns(self) -> List[Column]:
        """
        Describe columns in this row set.
        """

    @abc.abstractmethod
    def iter(self) -> Iterator['Row']:
        """
        Return a generator which yields rows from the underlying row stream or a table.
        """

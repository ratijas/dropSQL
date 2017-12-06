import abc
from typing import *
from typing.io import TextIO


from dropSQL.engine.row_set import *

__all__ = ['Formatter']


class Formatter(metaclass=abc.ABCMeta):
    @classmethod
    @abc.abstractmethod
    def with_row_set(cls, row_set: RowSet) -> 'Formatter':
        """
        Create a formatter of concrete type with given row set.
        """

    @abc.abstractmethod
    def format(self, f: TextIO) -> None:
        """
        Write self to the `f: TextIO` object which is basically a sink with `write(str)` method.
        """

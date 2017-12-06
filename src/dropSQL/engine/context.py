from .row import Row
from .types import *


class Context:
    """
    Evaluation context for expressions.
    """

    __slots__ = ['args', 'row']

    def __init__(self, row: Row, args: ARGS_TYPE) -> None:
        super().__init__()

        self.row = row
        self.args = args

    @classmethod
    def empty(cls) -> 'Context':
        """
        Empty context with empty row and w/o arguments for testing purposes.
        """
        return Context(Row.empty(), ())

    @classmethod
    def with_args(cls, args: ARGS_TYPE) -> 'Context':
        return Context(Row.empty(), args)

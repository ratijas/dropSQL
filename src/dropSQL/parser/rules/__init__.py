"""
Rule parsers work in conjunction with TokenStream type.

As a rule of thumb: if a rule failed to parse tokens,
it must leave stream in the same state as it was passed to it.
"""

from .rule import Rule

from .ty import *
from .existence import *
from .column_def import *
from .create_stmt import *
from .stmt import *

__all__ = [
    'Rule',

    'Ty',

    'Existence',
    'NonExistence',

    'ColumnDef',
    'ColumnsDef',
    'PrimaryKey',

    'CreateStmt',

    'Stmt',
]

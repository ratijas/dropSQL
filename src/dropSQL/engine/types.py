"""
Python types on which database engine operates using public interfaces.

Also some constants, e.g. master table name.
"""

from typing import *

__all__ = ['DB_TYPE', 'ARGS_TYPE', 'ROW_TYPE', 'MASTER_TABLE_NAME', 'MEMORY']

DB_TYPE = Union[str, int, float]
ARGS_TYPE = Tuple[DB_TYPE, ...]
ROW_TYPE = List[DB_TYPE]

MASTER_TABLE_NAME = 'autism'
MEMORY = ':memory:'

"""
Python types on which database engine operates using public interfaces.
"""

from typing import *

__all__ = ['DB_TYPE', 'ARGS_TYPE', 'ROW_TYPE']

DB_TYPE = Union[str, int, float]
ARGS_TYPE = Tuple[DB_TYPE, ...]
ROW_TYPE = List[DB_TYPE]

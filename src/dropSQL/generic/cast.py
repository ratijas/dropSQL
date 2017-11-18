from typing import *

from .result import *

__all__ = (
    'cast',
)

T = TypeVar('T')


def cast(o: object, ty: Type[T]) -> Result[T, None]:
    """
    Abstraction over builtin `isinstance` using `Result`.
    """
    if isinstance(o, ty):
        return Ok(o)
    else:
        return Err(None)

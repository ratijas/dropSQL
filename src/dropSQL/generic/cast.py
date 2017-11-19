from typing import *

from ..parser.expected import Expected
from .result import *

__all__ = (
    'cast',
    'drop',
)

T = TypeVar('T')


def cast(ty: Type[T]) -> Callable[[Any], Result[T, Expected]]:
    """
    Abstraction over builtin `isinstance` using `Result`.
    """

    def inner(o: Any) -> Result[T, Expected]:
        if isinstance(o, ty):
            return Ok(o)
        else:
            return Err(Expected([str(ty)], str(o)))

    return inner


def drop(_x: Any) -> None: pass

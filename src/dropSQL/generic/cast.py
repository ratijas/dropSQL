from typing import *

from ..parser.expected import Expected
from .result import *

__all__ = (
    'cast',
    'caster',
    'drop',
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


def caster(ty: Type[T]) -> Callable[[Any], Result[T, Expected]]:
    def inner(o: Any) -> Result[T, Expected]:
        return cast(o, ty).map_err(lambda _: Expected([str(ty)], str(o)))

    return inner


def drop(_x: Any) -> None: pass

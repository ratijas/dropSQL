from typing import *

from dropSQL.parser.expected import *
from .result import *

__all__ = ['Cast']

T = TypeVar('T')


# noinspection PyPep8Naming
def Cast(ty: Type[T]) -> Callable[[Any], Result[T, Expected]]:
    """
    Abstraction over builtin `isinstance` using `Result`.
    """

    def inner(o: Any) -> Result[T, Expected]:
        if isinstance(o, ty):
            return Ok(o)
        else:
            return Err(Expected([str(ty)], str(o)))

    return inner

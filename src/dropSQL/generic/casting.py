from typing import *

from .error import *
from .result import *
from .typevar import *

__all__ = ['Cast']


# noinspection PyPep8Naming
def Cast(ty: Type[T]) -> Callable[[Any], IResult[T]]:
    """
    Abstraction over builtin `isinstance` using `Result`.
    """

    def inner(o: Any) -> IResult[T]:
        if isinstance(o, ty):
            return IOk(o)
        else:
            return IErr(Syntax(ty.__name__, str(o)))

    return inner

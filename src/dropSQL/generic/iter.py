from typing import *

from .result import *

__all__ = (
    'IterOk',
)

T_co = TypeVar('T', covariant=True)
E_co = TypeVar('E', covariant=True)


class IterOk(Generic[T_co, E_co], Iterator[T_co], Iterable[T_co]):
    """
    Call `f` repeatedly until it returns `Err`.
    """

    def __init__(self, f: Callable[[], Result[T_co, E_co]]) -> None:
        self.f = f

    def __iter__(self) -> Iterator[T_co]:
        return self

    def __next__(self) -> T_co:
        x = self.f()
        if x:
            return x.ok()
        else:
            raise StopIteration

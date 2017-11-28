import abc
from typing import *

from .error import Error
from .typevar import *

__all__ = [
    'Result',
    'Ok',
    'Err',

    'IResult',
    'IOk',
    'IErr',
]


class Result(Generic[T, E], metaclass=abc.ABCMeta):
    """
    enum Result<T> {
        Ok(T),
        Err(E),
    }
    """

    def is_ok(self) -> bool:
        return isinstance(self, Ok)

    def is_err(self) -> bool:
        return isinstance(self, Err)

    def ok(self) -> T:
        raise NotImplementedError

    def err(self) -> E:
        raise NotImplementedError

    def ok_or(self, default: T) -> T:
        return default

    def err_or(self, default: E) -> E:
        return default

    def map(self, f: Callable[[T], U]) -> 'Result[U, E]':
        if isinstance(self, Ok):
            return Ok(f(self.ok()))
        else:
            return Err(self.err())

    def and_then(self, f: Callable[[T], 'Result[U, E]']) -> 'Result[U, E]':
        if isinstance(self, Ok):
            return f(self.ok())
        else:
            return Err(self.err())

    def __bool__(self) -> bool:
        return self.is_ok()


class Ok(Generic[T, E], Result[T, E]):
    def __init__(self, ok: T) -> None:
        self._ok = ok

    def ok(self) -> T:
        return self._ok

    def ok_or(self, default: T) -> T:
        return self.ok()

    def __repr__(self) -> str: return f'Result::Ok({self._ok!r})'


class Err(Generic[T, E], Result[T, E]):
    def __init__(self, error: E) -> None:
        self._err = error

    def err(self) -> E:
        return self._err

    def err_or(self, default: E) -> E:
        return self.err()

    def __repr__(self) -> str: return f'Result::Err({self._err!r})'


# stream-specific result type alias
IResult = Result[T, Error]
IOk = Ok[T, Error]
IErr = Err[T, Error]

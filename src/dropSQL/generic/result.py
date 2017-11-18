from typing import *

__all__ = (
    'Result',
    'Ok',
    'Err',
)

T = TypeVar('T')
E = TypeVar('E')
U = TypeVar('U')


class Result(Generic[T, E]):
    def is_ok(self): raise NotImplementedError

    def is_err(self): raise NotImplementedError

    def ok(self) -> T: raise NotImplementedError

    def ok_or(self, default: T) -> T: raise NotImplementedError

    def err(self) -> E: raise NotImplementedError

    def map(self, f: Callable[[T], U]) -> 'Result[U, E]': raise NotImplementedError

    def map_err(self, f: Callable[[E], U]) -> 'Result[T, U]': raise NotImplementedError

    def and_then(self, f: Callable[[T], 'Result[U, E]']) -> 'Result[U, E]': raise NotImplementedError

    def __bool__(self): return self.is_ok()

    def __repr__(self) -> str: raise NotImplementedError


class Ok(Generic[T, E], Result[T, E]):
    def __init__(self, ok: T) -> None:
        self._ok: T = ok

    def is_ok(self): return True

    def is_err(self): return False

    def ok(self) -> T: return self._ok

    def err(self) -> T: raise NotImplementedError(f'called `Result.err()` on an `Ok` value {self._ok}')

    def ok_or(self, default: T) -> T: return self.ok()

    def map(self, f: Callable[[T], U]) -> 'Result[U, E]': return Ok(f(self._ok))

    def map_err(self, f: Callable[[E], U]) -> 'Result[T, U]': return self

    def and_then(self, f: Callable[[T], 'Result[U, E]']) -> 'Result[U, E]': return f(self._ok)

    def __repr__(self) -> str: return f'Result.Ok( {repr(self._ok)} )'


class Err(Generic[T, E], Result[T, E]):
    def __init__(self, err: E) -> None:
        self._err: E = err

    def is_ok(self): return False

    def is_err(self): return True

    def ok(self) -> T: raise NotImplementedError(f'called `Result.ok()` on an `Err` value {self._err}')

    def err(self) -> E: return self._err

    def ok_or(self, default: T) -> T: return default

    def map(self, f: Callable[[T], U]) -> 'Result[U, E]': return self

    def map_err(self, f: Callable[[E], U]) -> 'Result[T, U]': return Err(f(self._err))

    def and_then(self, f: Callable[[T], 'Result[U, E]']) -> 'Result[U, E]': return Err(self._err)

    def __repr__(self) -> str: return f'Result.Err( {repr(self._err)} )'

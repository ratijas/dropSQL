from typing import *

__all__ = (
    'Result',
    'Token',
    'Error',
)


class Result:
    def is_ok(self):
        return isinstance(self, Token)

    def is_err(self):
        return isinstance(self, Error)


class Token(Result): pass


class Error(Result):
    def __init__(self, expected: List[str], got: str) -> None:
        self.expected = expected
        self.got = got

    def __str__(self) -> str:
        if len(self.expected) == 1:
            return f'expected {self.expected[0]}, got {self.got}.'
        else:
            return f'expected one of {", ".join(self.expected)}; got {self.got}.'

from typing import *

__all__ = (
    'Token',
    'Error',
)


class Token: pass


class Error:
    def __init__(self, expected: List[str], got: str) -> None:
        self.expected = expected
        self.got = got

    def __str__(self) -> str:
        if len(self.expected) == 1:
            return f'expected {self.expected[0]}, got {self.got}.'
        else:
            return f'expected one of {", ".join(self.expected)}; got {self.got}.'

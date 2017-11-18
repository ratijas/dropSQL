from typing import *

__all__ = (
    'Expected',
)


class Expected:
    def __init__(self, expected: List[str], got: str) -> None:
        self.expected = expected
        self.got = got

    def __str__(self) -> str:
        if len(self.expected) == 1:
            return f'Expected {self.expected[0]}; got {self.got}.'
        else:
            return f'Expected one of {", ".join(self.expected)}; got {self.got}.'

    def __repr__(self) -> str:
        return f'Expected( {repr(self.expected)}, {repr(self.got)} )'

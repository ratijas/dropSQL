from typing import *

__all__ = [
    'Expected',
    'Incomplete',
]


class Expected:
    """
    Error which represents expectations about parser's input, and
    the description of what was actually found. On the other hand,
    if input is incomplete (or no input at all as a special case),
    consider using the `Incomplete` subclass instead.
    """
    __slots__ = ('_expected', '_got')

    def __init__(self, expected: List[str], got: str) -> None:
        self._expected = expected
        self._got = got

    # like @property, but returns object itself
    def expected(self) -> List[str]:
        return self._expected

    def set_expected(self, expected: List[str]) -> 'Expected':
        self._expected = expected
        return self

    # no setter for `got` because unlike `expected`, which depends on level of perception,
    # it should not change as the error is propagated up the call chain.

    def got(self) -> str:
        return self._got

    def incomplete(self) -> bool:
        """ Is this an Incomplete kind of error? """
        return False

    def __str__(self) -> str:
        if len(self._expected) == 1:
            return f'Expected {self._expected[0]}; got {self.got()}.'
        else:
            return f'Expected one of {", ".join(self._expected)}; got {self.got()}.'

    def __repr__(self) -> str:
        return f'Expected( {repr(self._expected)}, {repr(self.got())} )'


class Incomplete(Expected):
    """ Specific `Expected` subclass for Incomplete case. """
    __slots__ = ()

    def __init__(self, expected: List[str]) -> None:
        super().__init__(expected, 'EOF')

    def incomplete(self) -> bool:
        return True

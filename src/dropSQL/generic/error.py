import abc

__all__ = [
    'Error',
    'Empty',
    'Incomplete',
    'Syntax',
]


class Error(metaclass=abc.ABCMeta):
    """
    enum Error {
      Empty,
      Incomplete,
      Syntax { expected: str, got: str },
    }
    """

    def is_empty(self) -> bool:
        return isinstance(self, Empty)

    def is_incomplete(self) -> bool:
        return isinstance(self, Incomplete)

    def is_syntax(self) -> bool:
        return isinstance(self, Syntax)

    def as_syntax(self) -> 'Syntax':
        if isinstance(self, Syntax):
            return self
        raise NotImplementedError

    def as_empty(self) -> 'Empty':
        if isinstance(self, Empty):
            return self
        raise NotImplementedError

    def empty_to_incomplete(self) -> 'Error':
        if isinstance(self, Empty):
            return Incomplete()

        else:
            return self

    def set_expected(self, expected: str) -> 'Error':
        return self


class Empty(Error):
    def __repr__(self) -> str: return 'Error::Empty'


class Incomplete(Error):
    def __repr__(self) -> str: return 'Error::Incomplete'


class Syntax(Error):
    def __init__(self, expected: str, got: str) -> None:
        self.expected = expected
        self.got = got

    def set_expected(self, expected: str) -> 'Error':
        self.expected = expected
        return self

    def __repr__(self) -> str: return f'Error::Syntax({self.expected!r}, {self.got!r})'

    def __str__(self) -> str: return f'Syntax error: expected {self.expected}, got {self.got}.'

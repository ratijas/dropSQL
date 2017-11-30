from io import StringIO

from dropSQL.generic import *
from .stream import Stream


class Characters(Stream[str]):
    def __init__(self, string: StringIO) -> None:
        super().__init__()

        self.string = string

    @classmethod
    def from_str(cls, source: str) -> 'Characters':
        return Characters(StringIO(source))

    def next_impl(self) -> IResult[T]:
        char = self.string.read(1)

        if char != '':
            return IOk(char)

        else:
            return IErr(Empty())

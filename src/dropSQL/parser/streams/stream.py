import abc
from typing import *

from dropSQL.generic import *


class Stream(Generic[T], metaclass=abc.ABCMeta):
    """
    Conceptually, endless stream of `Result`s.
    In practice, this means that after some `IOk` results
    it will start producing (normally the same over and over again) `IErr` results.
    """

    def __init__(self) -> None:
        self.cursor = 0
        self.buffer = []  # type: List[T]
        self.err = None  # type: Optional[Error]
        self._current = Err(Empty())  # type: IResult[T]

    def collect(self) -> IResult[List[T]]:
        """
        Iterate on self until `Err`.
        All `Err`s except `Empty` are propagated.
        `Err::Empty` is the normal way to finish the stream, so collected items are returned in a list.
        """

        xs = []
        self.next()
        while self.current().is_ok():
            xs.append(self.current().ok())
            self.next()

        else:
            err = self.current().err()

            if err.is_empty():
                return IOk(xs)
            else:  # err.is_syntax() or err.is_incomplete():
                return IErr(err)

    def current(self) -> IResult[T]:
        return self._current

    def next(self) -> IResult[T]:
        """
        rules:
         * stop at first `Err`
         * allow going back and forth
        """
        assert 0 <= self.cursor <= len(self.buffer)

        res: IResult[T]
        if self.cursor == len(self.buffer):
            if self.err is not None:
                res = IErr(self.err)

            else:
                res = self.next_impl()

                if res.is_err():
                    self.err = res.err()

                else:
                    self.buffer.append(res.ok())
                    self.cursor = len(self.buffer)

        else:  # self.cursor < len(self.buffer)
            item = self.buffer[self.cursor]
            self.cursor += 1
            res = IOk(item)

        self._current = res
        return res

    def peek(self) -> IResult[T]:
        current = self._current
        cursor = self.cursor
        err = self.err

        res = self.next()

        self._current = current
        self.cursor = cursor
        self.err = err

        return res

    def back(self, n: int = 1) -> None:
        assert self.cursor >= n > 0

        self.cursor -= n
        if self.cursor > 0:
            self._current = IOk(self.buffer[self.cursor - 1])
        else:
            self._current = IErr(Empty())

    @abc.abstractmethod
    def next_impl(self) -> IResult[T]:
        ...

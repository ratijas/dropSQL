from typing import *

from dropSQL.generic import *
from dropSQL.parser.streams import *
from dropSQL.parser.tokens import *
from .ast import Ast

__all__ = [
    'IfExists',
    'IfNotExists',
]


class IfExists(Ast):
    def to_sql(self) -> str:
        return 'if exists'

    @classmethod
    def from_sql(cls, tokens: Stream[Token]) -> IResult[Optional['IfExists']]:
        # next item must be an "if" token
        t = tokens.peek().and_then(Cast(If))
        if not t: return IOk(None)
        tokens.next()

        t = tokens.next().and_then(Cast(Exists))
        if not t: return IErr(t.err().empty_to_incomplete())

        return IOk(IfExists())


class IfNotExists(Ast):
    def to_sql(self) -> str:
        return 'if not exists'

    @classmethod
    def from_sql(cls, tokens: Stream[Token]) -> IResult[Optional['IfNotExists']]:
        # next item must be an "if" token
        t = tokens.peek().and_then(Cast(If))
        if not t: return IOk(None)
        tokens.next()

        t = tokens.next().and_then(Cast(Not))
        if not t: return IErr(t.err().empty_to_incomplete())

        t = tokens.next().and_then(Cast(Exists))
        if not t: return IErr(t.err().empty_to_incomplete())

        return IOk(IfNotExists())

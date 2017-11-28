from typing import *

from dropSQL.ast import *
from dropSQL.generic import *
from dropSQL.parser.tokens import *
from . import *

__all__ = (
    'Existence',
    'NonExistence',
)


class Existence(Rule[Optional[IfExists]]):
    """
    existence
        : /* empty */
        | "if" "exists"
        ;
    """

    @classmethod
    def parse(cls, ts: TokenStream) -> Result[Optional[IfExists], Expected]:
        t = ts.next().and_then(Cast(If))
        if not t:
            ts.undo()
            return Ok(None)

        t = ts.next().and_then(Cast(Exists))
        if not t: return Err(t.err())

        return Ok(IfExists())


class NonExistence(Rule[Optional[IfNotExists]]):
    """
    non_existence
        : /* empty */
        | "if" "not" "exists"
        ;
    """

    @classmethod
    def parse(cls, ts: TokenStream) -> Result[Optional[IfNotExists], Expected]:
        t = ts.next().and_then(Cast(If))
        if not t:
            ts.undo()
            return Ok(None)

        t = ts.next().and_then(Cast(Not))
        if not t: return Err(t.err())

        t = ts.next().and_then(Cast(Exists))
        if not t: return Err(t.err())

        return Ok(IfNotExists())

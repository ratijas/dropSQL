from typing import *

from dropSQL.generic import *
from dropSQL.parser.streams import *
from dropSQL.parser.tokens import *
from .ast import FromSQL
from .expression import Expression


class WhereFromSQL(FromSQL[Optional[Expression]]):
    @classmethod
    def from_sql(cls, tokens: Stream[Token]) -> IResult[Optional[Expression]]:
        t = tokens.peek().and_then(Cast(Where))
        if not t: return IOk(None)
        tokens.next().ok()

        e = Expression.from_sql(tokens)
        if not e: return IErr(e.err().empty_to_incomplete())

        return IOk(e.ok())

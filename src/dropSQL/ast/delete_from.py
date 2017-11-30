from typing import *

from dropSQL.generic import *
from dropSQL.parser.streams import *
from dropSQL.parser.tokens import *
from .ast import AstStmt
from .expression import Expression
from .identifier import Identifier
from .where import WhereFromSQL


class DeleteFrom(AstStmt):
    def __init__(self, table: Identifier, where: Optional[Expression]) -> None:
        super().__init__()

        self.table = table
        self.where = where

    def to_sql(self) -> str:
        stmt = '/delete from '
        stmt += str(self.table)

        if self.where is not None:
            stmt += ' /where '
            stmt += self.where.to_sql()

        stmt += ' /drop'
        return stmt

    @classmethod
    def from_sql(cls, tokens: Stream[Token]) -> IResult['DeleteFrom']:
        """
        /delete_stmt
            : "/delete" "from" /table_name /where_clause /drop
            ;
        """
        # next item must be the "/delete" token
        t = tokens.next().and_then(Cast(Delete))
        if not t: return IErr(t.err())

        t = tokens.next().and_then(Cast(From))
        if not t: return IErr(t.err().empty_to_incomplete())

        t = tokens.next().and_then(Cast(Identifier))
        if not t: return IErr(t.err().empty_to_incomplete())
        table = t.ok()

        t = WhereFromSQL.from_sql(tokens)
        if not t: return IErr(t.err().empty_to_incomplete())
        where = t.ok()

        t = tokens.next().and_then(Cast(Drop))
        if not t: return IErr(t.err().empty_to_incomplete())

        return IOk(DeleteFrom(table, where))

    def execute(self, db, args: List[Any] = ()) -> Result[None, None]:
        raise NotImplementedError

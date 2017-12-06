from typing import *

from dropSQL.engine.types import *
from dropSQL.generic import *
from dropSQL.parser.streams import *
from dropSQL.parser.tokens import *
from .ast import AstStmt
from .existence import IfExists


class DropTable(AstStmt):
    def __init__(self, if_exists: Optional[IfExists], table: Identifier) -> None:
        super().__init__()

        self.if_exists = if_exists
        self.table = table

    def to_sql(self) -> str:
        stmt = '/drop table '

        if self.if_exists is not None:
            stmt += self.if_exists.to_sql()
            stmt += ' '

        stmt += str(self.table)
        stmt += ' /drop'

        return stmt

    @classmethod
    def from_sql(cls, tokens: Stream[Token]) -> IResult['DropTable']:
        """
        /drop_stmt
            : "/drop" "table" existence /table_name /drop
            ;
        """
        # next item must be the first "/drop" token
        t = tokens.next().and_then(Cast(Drop))
        if not t: return IErr(t.err())

        t = tokens.next().and_then(Cast(Table))
        if not t: return IErr(t.err().empty_to_incomplete())

        t = IfExists.from_sql(tokens)
        if not t: return IErr(t.err().empty_to_incomplete())
        if_exists = t.ok()

        t = tokens.next().and_then(Cast(Identifier))
        if not t: return IErr(t.err().empty_to_incomplete())
        table = t.ok()

        t = tokens.next().and_then(Cast(Drop))
        if not t: return IErr(t.err().empty_to_incomplete())

        return IOk(DropTable(if_exists, table))

    def execute(self, db, args: ARGS_TYPE = ()) -> Result[bool, None]:
        from dropSQL.fs import DBFile
        db: DBFile = db

        for table in db.get_tables():
            name = table.get_table_name()

            if name == self.table:
                table.drop()
                return Ok(True)

        if self.if_exists is not None:  # error-tolerant
            return Ok(False)
        else:
            return Err(None)

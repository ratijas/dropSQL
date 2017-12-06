from typing import *

from dropSQL.engine.types import *
from dropSQL.generic import *
from dropSQL.parser.streams import *
from dropSQL.parser.tokens import *
from .ast import AstStmt
from .column_def import ColumnDef
from .existence import IfNotExists

if TYPE_CHECKING:
    from dropSQL import fs


class CreateTable(AstStmt):
    def __init__(self, if_not_exists: Optional[IfNotExists], table: Identifier, columns: List[ColumnDef]) -> None:
        super().__init__()

        self.if_not_exists = if_not_exists
        self.table = table
        self.columns = columns

    def to_sql(self) -> str:
        stmt = '/create table '

        if self.if_not_exists is not None:
            stmt += self.if_not_exists.to_sql()
            stmt += ' '

        stmt += str(self.table)
        stmt += ' (\n'

        for col in self.columns:
            stmt += '\t'
            stmt += col.to_sql()
            stmt += ',\n'
        stmt += ') /drop'

        return stmt

    @classmethod
    def from_sql(cls, tokens: Stream[Token]) -> IResult['CreateTable']:
        """
        /create_stmt
            : "/create" "table" existence /table_name "(" /columns_def ")" /drop
            ;
        """
        # next item must be the '/create' token
        t = tokens.next().and_then(Cast(Create))
        if not t: return IErr(t.err())

        t = tokens.next().and_then(Cast(Table))
        if not t: return IErr(t.err().empty_to_incomplete())

        t = IfNotExists.from_sql(tokens)
        if not t: return IErr(t.err().empty_to_incomplete())
        if_not_exists = t.ok()

        t = tokens.next().and_then(Cast(Identifier))
        if not t: return IErr(t.err().empty_to_incomplete())
        table = t.ok()

        t = tokens.next().and_then(Cast(LParen))
        if not t: return IErr(t.err().empty_to_incomplete())

        t = cls.parse_columns(tokens)
        if not t: return IErr(t.err().empty_to_incomplete())
        columns = t.ok()

        t = tokens.next().and_then(Cast(RParen))
        if not t: return IErr(t.err().empty_to_incomplete())

        t = tokens.next().and_then(Cast(Drop))
        if not t: return IErr(t.err().empty_to_incomplete())

        return IOk(CreateTable(if_not_exists, table, columns))

    @classmethod
    def parse_columns(cls, tokens: Stream[Token]) -> IResult[List[ColumnDef]]:
        """
        /columns_def
            : /column_def ("," /column_def)* ","?
            ;
        """
        # next item must be start of column definition
        # if return IOk, the next item must be ")"
        columns = []

        t = ColumnDef.from_sql(tokens)
        if not t: return IErr(t.err())
        columns.append(t.ok())

        # don't `next` comma yet.  maybe it is ")"
        while tokens.peek().and_then(Cast(Comma)):
            tokens.next()
            if tokens.peek().and_then(Cast(RParen)): break

            t = ColumnDef.from_sql(tokens)
            if not t: return IErr(t.err().empty_to_incomplete())
            columns.append(t.ok())

        t = tokens.peek().and_then(Cast(RParen))
        if not t: return IErr(t.err().empty_to_incomplete())

        return IOk(columns)

    def execute(self, db: 'fs.DBFile', args: ARGS_TYPE = ()) -> Result[bool, str]:
        t = db.get_table_by_name(self.table)
        if t:
            if self.if_not_exists is not None:  # error-tolerant
                return Ok(False)
            else:
                return Err(f'Table {self.table} exists')

        else:
            t = db.new_table()
            if not t: return Err(t.err())
            table = t.ok()

            table.set_table_name(self.table)

            for column in self.columns:
                table.add_column(column)

            return Ok(True)

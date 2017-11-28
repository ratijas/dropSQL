from dropSQL.ast import CreateTable
from dropSQL.generic import *
from dropSQL.parser.tokens import *
from . import *

__all__ = (
    'CreateStmt',
)


class CreateStmt(Rule[CreateTable]):
    """
    /create_stmt
        : "/create" "table" existence /table_name "(" /columns_def ")" /drop
        ;

    """

    @classmethod
    def parse(cls, ts: TokenStream) -> Result[CreateTable, Expected]:
        t = ts.next().and_then(Cast(Create))
        if not t: return Err(t.err())

        t = ts.next().and_then(Cast(Table))
        if not t: return Err(t.err())

        t = NonExistence.parse(ts)
        if not t: return Err(t.err().set_expected(['if', 'table name']))
        if_not_exists = t.ok()

        t = ts.next().and_then(Cast(Identifier))
        if not t: return Err(t.err().set_expected(['if', 'table name']))
        name = t.ok()

        t = ts.next().and_then(Cast(LParen))
        if not t: return Err(t.err())

        columns = ColumnsDef.parse(ts)
        if not columns: return Err(columns.err())
        columns = columns.ok()

        t = ts.next().and_then(Cast(RParen))
        if not t: return Err(t.err())

        t = ts.next().and_then(Cast(Drop))
        if not t: return Err(t.err())

        return Ok(CreateTable(if_not_exists, name, columns))

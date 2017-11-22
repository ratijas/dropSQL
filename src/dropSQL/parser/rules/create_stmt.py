from . import *

from dropSQL.parser.expected import *
from dropSQL.parser.tokens import *
from dropSQL.generic import *

from dropSQL.ast import CreateTable

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
        t = ts.gettok().and_then(cast(Create))
        if not t: return Err(t.err())

        t = ts.gettok().and_then(cast(Table))
        if not t: return Err(t.err())

        t = NonExistence.parse(ts)
        if not t: return Err(t.err().set_expected(['if', 'table name']))
        if_not_exists = t.ok()

        t = ts.gettok().and_then(cast(Identifier))
        if not t: return Err(t.err().set_expected(['if', 'table name']))
        name = t.ok()

        t = ts.gettok().and_then(cast(LParen))
        if not t: return Err(t.err())

        columns = ColumnsDef.parse(ts)
        if not columns: return Err(columns.err())
        columns = columns.ok()

        t = ts.gettok().and_then(cast(RParen))
        if not t: return Err(t.err())

        t = ts.gettok().and_then(cast(Drop))
        if not t: return Err(t.err())

        return Ok(CreateTable(if_not_exists, name, columns))

from typing import *

from dropSQL import ast
from dropSQL.parser.expected import Expected
from dropSQL.parser.tokens import *
from dropSQL.generic import *

from . import *

__all__ = (
    'ColumnDef',
    'ColumnsDef',
    'PrimaryKey',
)


class ColumnsDef(Rule[List[ast.ColumnDef]]):
    """
    /columns_def
        :               /column_def
        | /columns_def  /column_def
        ;
    """

    @classmethod
    def parse(cls, ts: TokenStream) -> Result[List[ast.ColumnDef], Expected]:
        columns = list(IterOk(lambda: ColumnDef.parse(ts)))
        if len(columns) > 0:
            return Ok(columns)
        else:
            return Err(ColumnDef.parse(ts).err())


class ColumnDef(Rule[ast.ColumnDef]):
    """
    /column_def
        : /column_name type /primary_key ","
        ;
    """

    @classmethod
    def parse(cls, ts: TokenStream) -> Result[ast.ColumnDef, Expected]:
        t = ts.gettok().and_then(cast(Identifier))
        if not t:
            ts.ungettok()
            return Err(Expected(['column name'], t.err().got))
        name = t.ok()

        t = Ty.parse(ts)
        if not t: return Err(t.err())
        ty = t.ok()

        t = PrimaryKey.parse(ts)
        if not t: return Err(t.err())
        is_primary_key = t.ok()

        t = ts.gettok().and_then(cast(Comma))
        if not t: return Err(t.err())

        return Ok(ast.ColumnDef(name, ty, is_primary_key))


class PrimaryKey(Rule[bool]):
    """
    /primary_key
        : /* empty */
        | "/primary" "key"
        ;
    """

    @classmethod
    def parse(cls, ts: TokenStream) -> Result[bool, Expected]:
        t = ts.gettok().and_then(cast(Primary))
        if not t:
            ts.ungettok()
            return Ok(False)

        t = ts.gettok().and_then(cast(Key))
        if not t: return Err(t.err())

        return Ok(True)

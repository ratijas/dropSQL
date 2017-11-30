from dropSQL.generic import *
from dropSQL.parser.streams import *
from dropSQL.parser.tokens import *
from .ast import Ast
from .ty import Ty


class ColumnDef(Ast):
    def __init__(self, name: Identifier, ty: Ty, is_primary_key: bool = False) -> None:
        super().__init__()

        self.name = name
        self.ty = ty
        self.is_primary_key = is_primary_key

    def to_sql(self) -> str:
        sql = str(self.name)
        sql += ' '
        sql += self.ty.to_sql()
        if self.is_primary_key:
            sql += ' /primary key'

        return sql

    @classmethod
    def from_sql(cls, tokens: Stream[Token]) -> IResult['ColumnDef']:
        """
        /column_def
            : /column_name type /primary_key
            ;
        """
        # the next item must be the column name
        t = tokens.next().and_then(Cast(Identifier))
        if not t: return IErr(t.err())
        name = t.ok()

        t = Ty.from_sql(tokens)
        if not t: return IErr(t.err().empty_to_incomplete())
        ty = t.ok()

        t = cls.parse_primary_key(tokens)
        if not t: return Err(t.err().empty_to_incomplete())
        is_primary_key = t.ok()

        return IOk(ColumnDef(name, ty, is_primary_key))

    @classmethod
    def parse_primary_key(cls, tokens: Stream[Token]) -> IResult[bool]:
        """
        /primary_key
            : /* empty */
            | "/primary" "key"
            ;
        """
        # next token MAY BE "/primary"
        t = tokens.peek().and_then(Cast(Primary))
        if not t: return IOk(False)
        tokens.next()

        t = tokens.next().and_then(Cast(Key))
        if not t: return IErr(t.err().empty_to_incomplete().set_expected('key'))

        return IOk(True)

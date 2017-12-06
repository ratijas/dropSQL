import abc
from typing import *

from dropSQL.engine.row_set import *
from dropSQL.generic import *
from dropSQL.parser.streams import *
from dropSQL.parser.tokens import *
from .ast import Ast
from .expression import Expression
from .identifier import Identifier

if TYPE_CHECKING:
    from dropSQL import fs


class Alias(Ast, metaclass=abc.ABCMeta):
    def __init__(self, alias: Optional[Identifier] = None) -> None:
        super().__init__()

        self.alias = alias


class AliasedTable(Alias):
    def __init__(self, name: Identifier, alias: Optional[Identifier] = None) -> None:
        super().__init__(alias)

        self.name = name

    def row_set(self, db: 'fs.DBFile') -> Result[RowSet, str]:
        r = db.get_row_set(self.name)
        if not r: return Err(r.err())
        rs = r.ok()

        if self.alias is not None:
            rs = RenameTableRowSet(rs, self.alias)

        return Ok(rs)

    def to_sql(self) -> str:
        s = str(self.name)
        if self.alias is not None:
            s += f' {str(self.alias)}'
        return s

    @classmethod
    def from_sql(cls, tokens: Stream[Token]) -> IResult['AliasedTable']:
        """
        /aliased_table
            : /table_name /table_alias
            ;

        /table_alias
            : /* empty */
            | /identifier
            ;
        """
        t = tokens.next().and_then(Cast(Identifier))
        if not t: return IErr(t.err())
        name = t.ok()

        alias = None
        t = tokens.peek().and_then(Cast(Identifier))
        if t:
            tokens.next()
            alias = t.ok()

        return IOk(AliasedTable(name, alias))


class AliasedExpression(Alias):
    def __init__(self, expression: Expression, alias: Optional[Identifier] = None) -> None:
        super().__init__(alias)

        self.expression = expression

    def to_sql(self) -> str:
        expr: str = self.expression.to_sql()
        if self.alias is not None:
            expr += f' /as {str(self.alias)}'
        return expr

    @classmethod
    def from_sql(cls, tokens: Stream[Token]) -> IResult['AliasedExpression']:
        """
        /result_column
            : "*"
            | /aliased_expression
            ;

        /aliased_expression
            : expr /expression_alias
            ;

        /expression_alias
            : /* empty */
            | /as /identifier
            ;
        """
        t = Expression.from_sql(tokens)
        if not t: return IErr(t.err())
        expr = t.ok()

        alias: Optional[Identifier] = None
        t = tokens.peek().and_then(Cast(As))
        if t:
            tokens.next()
            t = tokens.next().and_then(Cast(Identifier))
            if not t: return IErr(t.err().empty_to_incomplete())
            alias = t.ok()

        return IOk(AliasedExpression(expr, alias))

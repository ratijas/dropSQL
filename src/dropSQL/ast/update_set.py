from typing import *

from dropSQL.ast.comma_separated import CommaSeparated
from dropSQL.generic import *
from dropSQL.parser.streams import *
from dropSQL.parser.tokens import *
from .ast import AstStmt, FromSQL
from .expression import Expression
from .identifier import Identifier
from .where import WhereFromSQL


class UpdateSet(AstStmt):
    def __init__(self,
                 table: Identifier,
                 assign: List[Tuple[Identifier, Expression]],
                 where: Optional[Expression]) -> None:
        super().__init__()

        self.table = table
        self.assign = assign
        self.where = where

    def to_sql(self) -> str:
        stmt = '/update '
        stmt += str(self.table)
        stmt += ' /set '

        assignments = []
        for column, value in self.assign:
            buf = ''
            buf += str(column)
            buf += ' = '
            buf += value.to_sql()
            assignments.append(buf)
        stmt += ', '.join(assignments)

        if self.where is not None:
            stmt += ' /where '
            stmt += self.where.to_sql()

        stmt += ' /drop'
        return stmt

    @classmethod
    def from_sql(cls, tokens: Stream[Token]) -> IResult['UpdateSet']:
        """
        /update_stmt
            : "/update" /table_name "set" /assignments /where_clause /drop
            ;
        """
        # next item must be the '/create' token
        t = tokens.next().and_then(Cast(Update))
        if not t: return IErr(t.err())

        t = tokens.next().and_then(Cast(Identifier))
        if not t: return IErr(t.err().empty_to_incomplete())
        table = t.ok()

        t = tokens.next().and_then(Cast(SetKw))
        if not t: return IErr(t.err().empty_to_incomplete())

        t = CommaSeparated(Assignment, tokens).collect()
        if not t: return IErr(t.err().empty_to_incomplete())
        assign = t.ok()

        t = WhereFromSQL.from_sql(tokens)
        if not t: return IErr(t.err().empty_to_incomplete())
        where = t.ok()

        t = tokens.next().and_then(Cast(Drop))
        if not t: return IErr(t.err().empty_to_incomplete())

        return IOk(UpdateSet(table, assign, where))

    def execute(self, db, args: List[Any] = ()) -> Result[None, None]:
        raise NotImplementedError


class Assignment(FromSQL[Tuple[Identifier, Expression]]):
    @classmethod
    def from_sql(cls, tokens: Stream[Token]) -> IResult[Tuple[Identifier, Expression]]:
        """
        /assignment
            : /column_name "=" expr
            ;
        """
        t = tokens.next().and_then(Cast(Identifier))
        if not t: return IErr(t.err().empty_to_incomplete())
        lvalue = t.ok()

        t = tokens.next().and_then(Cast(Operator))
        if not t: return IErr(t.err().empty_to_incomplete())
        if t.ok().operator != Operator.EQ: return IErr(Syntax('=', str(t)))

        t = Expression.from_sql(tokens)
        if not t: return IErr(t.err().empty_to_incomplete())
        e = t.ok()

        return IOk((lvalue, e))

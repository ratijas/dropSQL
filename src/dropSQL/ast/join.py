import abc
from typing import *

from dropSQL.engine.row_set import *
from dropSQL.engine.types import *
from dropSQL.generic import *
from dropSQL.parser.streams import *
from dropSQL.parser.tokens import *
from .alias import AliasedTable
from .ast import *
from .expression import Expression

if TYPE_CHECKING:
    from dropSQL import fs

__all__ = [
    'JoinClausesParser',
    'JoinAst',
    'CrossJoin',
    'InnerJoin',
]


class JoinClausesParser(FromSQL[List['JoinAst']]):
    @classmethod
    def from_sql(cls, tokens: Stream[Token]) -> IResult[List['JoinAst']]:
        """
        /from_body
            : /aliased_table /join_clauses
            ;

        /join_clauses
            : /* empty */
            | /join_clauses /join_clause
            ;
        """
        # take while next is not err.  if err is Empty, return the list, otherwise return error.
        joins: List[JoinAst] = []

        join = JoinAst.from_sql(tokens)
        while join.is_ok():
            joins.append(join.ok())
            join = JoinAst.from_sql(tokens)

        if join.err().is_empty(): return IOk(joins)
        return IErr(join.err())


class JoinAst(Ast, FromSQL['JoinAst'], metaclass=abc.ABCMeta):
    def __init__(self, table: AliasedTable) -> None:
        super().__init__()

        self.table = table

    @abc.abstractmethod
    def join(self, lhs: RowSet, db: 'fs.DBFile', args: ARGS_TYPE = ()) -> Result[RowSet, str]:
        """
        Join `lhs` on the left with self on the right.
        """

    @classmethod
    def from_sql(cls, tokens: Stream[Token]) -> IResult['JoinAst']:
        """
        /join_clause
            : /cross_join
            | /inner_join
            ;
        """
        t = tokens.peek()
        if not t: return IErr(t.err())
        tok = t.ok()

        if isinstance(tok, Comma):
            return CrossJoin.from_sql(tokens)

        if isinstance(tok, Join):
            return InnerJoin.from_sql(tokens)

        return IErr(Empty())


class CrossJoin(JoinAst, FromSQL['CrossJoin']):
    def __init__(self, table: AliasedTable) -> None:
        super().__init__(table)

    def join(self, lhs: RowSet, db: 'fs.DBFile', args: ARGS_TYPE = ()) -> Result[RowSet, str]:
        rhs = self.table.row_set(db)
        if not rhs: return Err(rhs.err())

        rs = CrossJoinRowSet(lhs, rhs.ok())

        return Ok(rs)

    def to_sql(self) -> str:
        join = ', '
        join += self.table.to_sql()

        return join

    @classmethod
    def from_sql(cls, tokens: Stream[Token]) -> IResult['JoinAst']:
        """
        /cross_join
            : "," /aliased_table
            ;
        """
        t = tokens.next().and_then(Cast(Comma))
        if not t: return IErr(t.err())

        t = AliasedTable.from_sql(tokens)
        if not t: return IErr(t.err().empty_to_incomplete())
        table = t.ok()

        return IOk(CrossJoin(table))


class InnerJoin(CrossJoin, FromSQL['InnerJoin']):
    def __init__(self, table: AliasedTable, constraint: Expression) -> None:
        super().__init__(table)

        self.constraint = constraint

    def join(self, lhs: RowSet, db: 'fs.DBFile', args: ARGS_TYPE = ()) -> Result[RowSet, str]:
        r = self.table.row_set(db)
        if not r: return Err(r.err())
        rhs = r.ok()

        return Ok(InnerJoinRowSet(lhs, rhs, self.constraint, args))

    def to_sql(self) -> str:
        join = ' /join '
        join += self.table.to_sql()

        if self.constraint is not None:
            join += ' /on '
            join += self.constraint.to_sql()

        return join

    @classmethod
    def from_sql(cls, tokens: Stream[Token]) -> IResult['InnerJoin']:
        """
        /inner_join
            : "/join" /aliased_table "/on" expr
            ;
        """
        t = tokens.next().and_then(Cast(Join))
        if not t: return IErr(t.err())

        t = AliasedTable.from_sql(tokens)
        if not t: return IErr(t.err().empty_to_incomplete())
        table = t.ok()

        t = tokens.next().and_then(Cast(On))
        if not t: return IErr(t.err().empty_to_incomplete())

        t = Expression.from_sql(tokens)
        if not t: return IErr(t.err().empty_to_incomplete())
        constraint = t.ok()

        return IOk(InnerJoin(table, constraint))

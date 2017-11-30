from typing import *

from dropSQL.generic import *
from dropSQL.parser.streams import *
from dropSQL.parser.tokens import *
from .alias import AliasedTable
from .ast import AstStmt
from .comma_separated import CommaSeparated
from .expression import Expression
from .join import JoinAst
from .result_column import ResultColumn
from .where import WhereFromSQL


class SelectFrom(AstStmt):
    def __init__(self,
                 columns: List[ResultColumn],
                 table: AliasedTable,
                 joins: List[JoinAst] = list(),
                 where: Optional[Expression] = None) -> None:
        super().__init__()

        self.columns = columns
        self.table = table
        self.joins = joins
        self.where = where

    def to_sql(self) -> str:
        stmt = '/select '

        stmt += ', '.join([column.to_sql() for column in self.columns])
        stmt += ' /from '
        stmt += self.table.to_sql()

        if len(self.joins) != 0:
            stmt += ''.join([join.to_sql() for join in self.joins])

        if self.where is not None:
            stmt += ' /where '
            stmt += self.where.to_sql()

        stmt += ' /drop'

        return stmt

    @classmethod
    def from_sql(cls, tokens: Stream[Token]) -> IResult['SelectFrom']:
        """
        /select_stmt
            : "/select" /result_columns
                 "from" /from_body
                        /where_clause
                        /drop
            ;
        """
        # next item must be the '/select' token
        t = tokens.next().and_then(Cast(Select))
        if not t: return IErr(t.err())

        t = CommaSeparated(ResultColumn, tokens).collect()
        if not t: return IErr(t.err().empty_to_incomplete())
        columns = t.ok()

        t = tokens.next().and_then(Cast(From))
        if not t: return IErr(t.err().empty_to_incomplete())

        t = AliasedTable.from_sql(tokens)
        if not t: return IErr(t.err().empty_to_incomplete())
        table = t.ok()

        # TODO: joins

        t = WhereFromSQL.from_sql(tokens)
        if not t: return IErr(t.err().empty_to_incomplete())
        where = t.ok()

        t = tokens.next().and_then(Cast(Drop))
        if not t: return IErr(t.err().empty_to_incomplete())

        return IOk(SelectFrom(columns, table, where=where))

    def execute(self, db, args: List[Any] = ()) -> Result[None, None]:
        raise NotImplementedError

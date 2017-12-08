from typing import *

from dropSQL.ast.comma_separated import CommaSeparated
from dropSQL.engine.context import Context
from dropSQL.engine.row import Row
from dropSQL.engine.row_set import *
from dropSQL.engine.types import *
from dropSQL.generic import *
from dropSQL.parser.streams import *
from dropSQL.parser.tokens import *
from .ast import AstStmt, FromSQL
from .expression import Expression
from .identifier import Identifier
from .where import WhereFromSQL

if TYPE_CHECKING:
    from dropSQL import fs


class UpdateSet(AstStmt):
    def __init__(self,
                 table: Identifier,
                 assign: List[Tuple[Identifier, Expression]],
                 where: Optional[Expression]) -> None:
        super().__init__()

        self.table = table
        self.assignments = assign
        self.where = where

    def to_sql(self) -> str:
        stmt = '/update '
        stmt += str(self.table)
        stmt += ' /set '

        assignments = []
        for column, value in self.assignments:
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
        # next item must be the '/update' token
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

    def execute(self, db: 'fs.DBFile', args: ARGS_TYPE = ()) -> Result[None, None]:
        """
        update algorithm:

        get table
        reorder expressions
        apply "where" clause
        for each row:
            update values

        Set of columns in 'update set' statement must be a non-strict subset of a column set of the table.
        """
        if self.table == Identifier('autism'): return Err('Can not operate on master table')

        t = db.get_table_by_name(self.table)
        if not t: return Err(t.err())
        table = t.ok()

        rs = TableRowSet(table)
        if self.where is not None:
            rs = FilteredRowSet(rs, self.where, args)

        t = self.make_transformations(rs)
        if not t: return Err(t.err())
        transformation = t.ok()

        count = 0
        for row in rs.iter():
            r = update_row(row, transformation, args)
            if not r: return Err(r.err())
            new_row = r.ok()

            t = table.update(new_row, row.id)
            if not t: return Err(t.err())
            count += 1

        return Ok(count)

    def make_transformations(self, rs: RowSet) -> Result[List[Optional[Expression]], str]:
        assignments = dict(self.assignments)
        if len(assignments) != len(self.assignments): return Err(f'Duplicate columns detected')

        transformation: List[Optional[Expression]] = []
        for column in rs.columns():
            transformation.append(assignments.pop(column.name, None))

        assert len(transformation) == len(rs.columns())
        if len(assignments) != 0: return Err(f'Unexpected column(s): ' + ', '.join(map(str, assignments.keys())))

        return Ok(transformation)


def update_row(row: Row, transformation: List[Optional[Expression]], args: ARGS_TYPE) -> Result[ROW_TYPE, str]:
    r: ROW_TYPE = []

    for cell, expr in zip(row.data, transformation):
        if expr is None:
            r.append(cell)

        else:
            v = expr.eval_with(Context(row, args))
            if not v: return Err(v.err())
            val = v.ok()

            r.append(val)

    return Ok(r)


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

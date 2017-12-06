from typing import *

from dropSQL.engine.context import Context
from dropSQL.engine.types import *
from dropSQL.generic import *
from dropSQL.parser.streams import *
from dropSQL.parser.tokens import *
from .ast import AstStmt, FromSQL
from .comma_separated import CommaSeparated
from .expression import Expression

if TYPE_CHECKING:
    from dropSQL import fs

ValueType = List[Expression]
ValuesType = List[ValueType]


def count_check(expected: int, values: ValuesType) -> IResult[None]:
    for value in values:
        if len(value) != expected:
            return IErr(Syntax(f'{expected} expressions', str(len(value))))
    return IOk(None)


class InsertInto(AstStmt, FromSQL['InsertInto']):
    def __init__(self, table: Identifier, columns: List[Identifier], values: ValuesType) -> None:
        super().__init__()

        self.table = table
        self.columns = columns
        self.values = values

    def to_sql(self) -> str:
        stmt = '/insert into '
        stmt += str(self.table)

        stmt += ' ('
        stmt += ', '.join(str(column) for column in self.columns)
        stmt += ') values '

        values: List[str] = []
        for value in self.values:
            buf = '('
            buf += ', '.join(expression.to_sql() for expression in value)
            buf += ')'
            values.append(buf)

        stmt += ', '.join(values)
        stmt += ' /drop'

        return stmt

    @classmethod
    def from_sql(cls, tokens: Stream[Token]) -> IResult['InsertInto']:
        """
        /insert_stmt
            : "/insert" "into" /table_name "(" /columns_names ")" "values" values /drop
            ;
        """
        # next item must be the "/insert" token
        t = tokens.next().and_then(Cast(Insert))
        if not t: return IErr(t.err())

        t = tokens.next().and_then(Cast(Into))
        if not t: return IErr(t.err().empty_to_incomplete())

        t = tokens.next().and_then(Cast(Identifier))
        if not t: return IErr(t.err().empty_to_incomplete())
        table = t.ok()

        t = tokens.next().and_then(Cast(LParen))
        if not t: return IErr(t.err().empty_to_incomplete())

        t = CommaSeparated(IdentFromSQL, tokens).collect()
        if not t: return IErr(t.err().empty_to_incomplete())
        columns = t.ok()

        t = tokens.next().and_then(Cast(RParen))
        if not t: return IErr(t.err().empty_to_incomplete())

        t = tokens.next().and_then(Cast(Values))
        if not t: return IErr(t.err().empty_to_incomplete())

        t = CommaSeparated(ValueFromSQL, tokens).collect()
        if not t: return IErr(t.err().empty_to_incomplete())
        values = t.ok()

        t = tokens.next().and_then(Cast(Drop))
        if not t: return IErr(t.err().empty_to_incomplete())

        c = count_check(len(columns), values)
        if not c: return IErr(c.err())

        return IOk(InsertInto(table, columns, values))

    def execute(self, db: 'fs.DBFile', args: ARGS_TYPE = ()) -> Result[None, str]:
        # 1. find table by name
        # 2. reorder columns in query according to table
        # 3. underlying insert
        t = db.get_table_by_name(self.table)
        if not t: return Err(t.err())
        table = t.ok()

        t = self.transition_vector(table)
        if not t: return Err(t.err())
        transition = t.ok()

        ctx = Context.empty()
        ctx.args = args

        for value in self.values:
            if len(value) != len(self.columns): return Err('#values != number of columns')

            row: ROW_TYPE = [None] * len(self.columns)
            for i, expr in enumerate(value):

                res = expr.eval_with(ctx)
                if not res: return Err(res.err())
                item = res.ok()

                row[transition[i]] = item

            res = table.insert(row)
            if not res: return Err(res.err())

        return Ok(None)

    def transition_vector(self, table: 'fs.Table') -> Result[List[int], str]:
        table_columns = table.get_columns()

        added: Set[Identifier] = set()
        transitions: List[int] = []

        for i, column in enumerate(self.columns):
            if column in added: return Err(f'Column {column} duplicate')

            for j, t_column in enumerate(table_columns):
                if column == t_column.name:
                    added.add(column)
                    transitions.append(j)
                    break

            else:
                return Err(f'Column {column} does not exist in table')

        assert len(transitions) == len(self.columns)
        return Ok(transitions)


class IdentFromSQL(FromSQL[Identifier]):
    @classmethod
    def from_sql(cls, tokens: Stream[Token]) -> IResult[Identifier]:
        t = tokens.next().and_then(Cast(Identifier))
        if not t: return IErr(t.err().empty_to_incomplete())

        return IOk(t.ok())


class ValueFromSQL(FromSQL[ValueType]):
    @classmethod
    def from_sql(cls, tokens: Stream[Token]) -> IResult[ValueType]:
        t = tokens.next().and_then(Cast(LParen))
        if not t: return IErr(t.err().empty_to_incomplete())

        t = CommaSeparated(Expression, tokens).collect()
        if not t: return IErr(t.err().empty_to_incomplete())
        value = t.ok()

        t = tokens.next().and_then(Cast(RParen))
        if not t: return IErr(t.err().empty_to_incomplete())

        return IOk(value)

from typing import *

from dropSQL.generic import *
from dropSQL.parser.streams import *
from dropSQL.parser.tokens import *
from .ast import AstStmt, FromSQL
from .expression import Expression

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

    def execute(self, db, args: List[Any] = ()) -> Result[None, None]:
        raise NotImplementedError


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


class CommaSeparated(Generic[T], Stream[T]):
    def __init__(self, ty: Type[FromSQL[T]], tokens: Stream[Token]):
        super().__init__()

        self.ty = ty
        self.tokens = tokens
        self.first = True

    def next_impl(self) -> IResult[T]:
        if self.first:
            self.first = False

        else:
            t = self.tokens.peek().and_then(Cast(Comma))
            if not t: return IErr(Empty())
            self.tokens.next()

        return self.ty.from_sql(self.tokens)

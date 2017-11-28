from dropSQL.ast import *
from dropSQL.generic import *
from dropSQL.parser.tokens import *

from . import *


class Stmt(Rule[AstStmt]):
    expected = list(map(str, [Create, Drop, Insert, Delete, Update, Select]))

    @classmethod
    def parse(cls, ts: TokenStream) -> Result[AstStmt, Expected]:
        t = ts.peek()

        if t.and_then(Cast(Create)):
            return CreateStmt.parse(ts)

        elif t.and_then(Cast(Drop)):
            return DropStmt.parse(ts)

        elif t.and_then(Cast(Insert)):
            return InsertStmt.parse(ts)

        elif t.and_then(Cast(Delete)):
            return DeleteStmt.parse(ts)

        elif t.and_then(Cast(Update)):
            return UpdateStmt.parse(ts)

        elif t.and_then(Cast(Select)):
            return SelectStmt.parse(ts)

        elif not t:
            return Err(t.err().set_expected(cls.expected))

        else:
            return Err(Expected(cls.expected, str(t.ok())))

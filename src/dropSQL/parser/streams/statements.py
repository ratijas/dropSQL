from dropSQL.ast.stmt import *
from dropSQL.generic import *
from dropSQL.parser.tokens import *
from .stream import Stream
from .tokens import Tokens


class Statements(Stream[AstStmt]):
    def __init__(self, tokens: Stream[Token]) -> None:
        super().__init__()

        self.tokens = tokens

    @classmethod
    def from_str(cls, source: str) -> 'Statements':
        return Statements(Tokens.from_str(source))

    def next_impl(self) -> IResult[AstStmt]:

        t = self.tokens.peek()
        if not t: return Err(t.err())
        tok = t.ok()

        if isinstance(tok, Drop):
            return DropTable.from_sql(self.tokens)

        # elif isinstance(tok, Select): ...

        else:
            return Err(Syntax('/drop', str(tok)))

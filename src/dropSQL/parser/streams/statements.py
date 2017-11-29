from dropSQL.ast import *
from dropSQL.generic import *
from dropSQL.parser.tokens import *
from .stream import Stream
from .tokens import Tokens


class Statements(Stream[ast.AstStmt]):
    def __init__(self, tokens: Stream[Token]) -> None:
        super().__init__()

        self.tokens = tokens

    @classmethod
    def from_str(cls, source: str) -> 'Statements':
        return Statements(Tokens.from_str(source))

    def next_impl(self) -> IResult[ast.AstStmt]:
        return IErr(Empty())

        # tok = self.tokens.next()
        # if tok.is_err(): return Err(tok.err())
        #
        # tok = tok.ok()
        #
        # if isinstance(tok, Create):
        #     return CreateTableStmt.parse(self.tokens)
        #
        # else:
        #     return Err(Syntax('/create', str(tok)))

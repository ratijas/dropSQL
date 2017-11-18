from ..tokens import *

__all__ = (
    'TokenStream',
)


class TokenStream:
    def __init__(self, stream: Stream) -> None:
        super().__init__()

        self.tokens = []
        tok = next_token(stream)
        while not isinstance(tok, Error):
            self.tokens.append(tok)
            tok = next_token(stream)

        self.cursor: int = 0
        self.done: bool = False  # once gettok on exhausted stream, this flag will always be True.

    def gettok(self) -> Result:
        if self.cursor >= len(self.tokens):
            tok = Error(['token'], 'EOF')
            self.done = True
        else:
            tok = self.tokens[self.cursor]
            self.cursor += 1

        assert ((isinstance(tok, Error) and self.done) or
                (isinstance(tok, Token) and not self.done))
        return tok

    def ungettok(self) -> None:
        if not self.done and self.cursor > 0:
            self.cursor -= 1

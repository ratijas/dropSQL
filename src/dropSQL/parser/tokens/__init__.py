from typing import *

from dropSQL.generic import *
from dropSQL.parser.expected import *
from .token import Token
from .identifier import IdentifierBase, Identifier, Reserved
from . import reserved as __reserved
from .reserved import *
from .operator import Operator
from .literal import Literal, Integer, Float, String
from .placehodler import Placeholder
from .comma import Comma
from .paren import LParen, RParen

__all__ = (
    'Token',

    'Stream',
    'TokenStream',
    'next_token',

    'IdentifierBase',
    'Identifier',
    'Reserved',

    # reserved
    'As',
    'Create',
    'Drop',
    'Delete',
    'Select',
    'From',
    'Join',
    'On',
    'Table',
    'If',
    'Not',
    'Exists',
    'Primary',
    'Key',
    'Insert',
    'Into',
    'Update',
    'Set',
    'Values',
    'Where',

    'Operator',

    'Literal',
    'Integer',
    'Float',
    'String',

    'Placeholder',

    'Comma',
    'LParen',
    'RParen',
)

EMPTY = ''


class Stream:
    """
    simple getch/ungetch stream of characters.
    """

    def __init__(self, data: str) -> None:
        super().__init__()
        self.data: str = data
        self.cursor: int = 0
        self.done = False  # once getch on exhausted stream, this flag will always be True.

    def getch(self) -> Result[str, EOF]:
        """ return next character in a stream or Error. """
        if self.cursor >= len(self.data):
            char = Err(EOF(['char']))
            self.done = True

        else:
            char = Ok(self.data[self.cursor])
            self.cursor += 1

        assert ((char.is_err() and char.err().eof() and self.done) or
                (len(char.ok()) == 1 and not self.done))
        return char

    def ungetch(self) -> None:
        if not self.done and self.cursor > 0:
            self.cursor -= 1


class TokenStream:
    def __init__(self, stream: Stream) -> None:
        super().__init__()

        self.tokens = list(IterOk(lambda: next_token(stream)))
        self.error = next_token(stream).err()

        self.cursor: int = 0
        self.done: bool = False  # once gettok on exhausted stream, this flag will always be True.

    def gettok(self) -> Result[Token, Expected]:
        if self.cursor >= len(self.tokens):
            tok = Err(self.error)
            self.done = True

        else:
            tok = Ok(self.tokens[self.cursor])
            self.cursor += 1

        assert ((tok.is_ok() and not self.done) or
                (tok.is_err() and self.done))
        return tok

    def ungettok(self) -> None:
        if not self.done and self.cursor > 0:
            self.cursor -= 1


keywords: Dict[str, Token] = {
    k.lower(): getattr(__reserved, k)()
    for k in __reserved.__all__
}
keywords.update({
    'and': Operator('/and'),
    'or' : Operator('/or'),
})


def next_token(stream: Stream, skip_space: bool = True) -> Result[Token, Expected]:
    """
    Extract next token from character stream.
    """
    if skip_space:
        skip_whitespaces(stream)

    char = stream.getch().ok_or(EMPTY)
    next_char = stream.getch().ok_or(EMPTY)
    stream.ungetch()

    if char == EMPTY:
        return Err(EOF(['token']))

    elif char == ',':
        return Ok(Comma())

    elif char == '(':
        return Ok(LParen())

    elif char == ')':
        return Ok(RParen())

    elif char.isalpha() or (char == '/' and next_char.isalpha()):
        return Ok(tok_identifier(stream, char))

    elif char.isdigit() or char == '.':
        num = char
        char = stream.getch().ok_or(EMPTY)

        while char.isdigit() or char == '.':
            num += char
            char = stream.getch().ok_or(EMPTY)

        stream.ungetch()
        if '.' in num:
            try:
                f = float(num)
                return Ok(Float(f))
            except (ValueError, OverflowError) as _:
                return Err(Expected(['float'], num))
        else:
            try:
                i = int(num, 10)
                return Ok(Integer(i))
            except (ValueError, OverflowError) as _:
                return Err(Expected(['int'], num))

    elif char == '-':
        if next_char == '-':
            # comment, skip until EOL of EOF
            while char != EMPTY and char != '\n' and char != '\r':
                char = stream.getch().ok_or(EMPTY)

            return next_token(stream)

        else:
            return Ok(Operator('-'))

    elif char == '\'':
        return tok_string(stream)

    # <= /= >=
    elif char in '</>' and next_char == '=':
        stream.getch()  # consume next_char
        return Ok(Operator(char + next_char))

    # * / + - < = >
    elif char in ('*', '/', '+', '-', '<', '=', '>'):
        return Ok(Operator(char))

    elif char == '?':
        t = next_token(stream, False).and_then(cast(Integer))
        if not t: return Err(t.err())

        index = t.ok()
        return Ok(Placeholder(index.value))

    else:
        stream.ungetch()
        return Err(Expected(['token'], char))


def tok_identifier(stream: Stream, char: str) -> Token:
    slash = char == '/'
    if slash:
        char = stream.getch().ok_or(EMPTY)

    ident = ''
    while char.isalnum() or char == '_':
        ident += char
        char = stream.getch().ok_or(EMPTY)
    stream.ungetch()

    keyword = keywords.get(ident.lower(), None)
    if keyword is not None:
        return keyword

    else:
        return Identifier(ident, slash)


def tok_string(stream: Stream) -> Result[String, EOF]:
    string = ''
    char = stream.getch().ok_or(EMPTY)
    while char != EMPTY and char != '\'':
        if char == '\\':
            # escape sequence
            char = stream.getch().ok_or(EMPTY)
        string += char
        char = stream.getch().ok_or(EMPTY)

    # no ungetch because we want to consume the closing quote

    if char == EMPTY:
        return Err(EOF(['string literal']))
    else:
        return Ok(String(string))


def skip_whitespaces(stream: Stream) -> None:
    while True:
        char = stream.getch()
        if char.is_err(): break
        if not char.ok().isspace():
            stream.ungetch()
            break

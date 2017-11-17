from typing import *
from .common import *
from .identifier import Identifier
from .reserved import *
from .operator import Operator
from .literal import Literal, Integer, Float, String
from .placehodler import Placeholder
from .comma import Comma
from .paren import LParen, RParen

__all__ = (
    'Result',
    'Error',
    'Token',
    'Stream',
    'next_token',

    'Identifier',

    'Create',
    'Drop',
    'Table',
    'If',
    'Not',
    'Exists',
    'Values',
    'Primary',
    'Key',
    'Insert',
    'Into',

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

EOF = ''


class Stream:
    """
    simple getch/ungetch stream of characters.
    """

    def __init__(self, data: str) -> None:
        super().__init__()
        self.data: str = data
        self.cursor: int = 0
        self.done = False  # once getch on exhausted stream, this flag will always be True.

    def getch(self) -> str:
        """ return next character in a stream or EOF constant. """
        if self.cursor >= len(self.data):
            char = EOF
            self.done = True
        else:
            char = self.data[self.cursor]
            self.cursor += 1

        assert ((char == EOF and self.done) or
                (len(char) == 1 and not self.done))
        return char

    def ungetch(self):
        if not self.done and self.cursor > 0:
            self.cursor -= 1


keywords: Dict[str, Token] = {
    'create' : Create(),
    'drop'   : Drop(),
    'table'  : Table(),
    'if'     : If(),
    'not'    : Not(),
    'exists' : Exists(),
    'values' : Values(),
    'primary': Primary(),
    'key'    : Key(),
    'insert' : Insert(),
    'into'   : Into(),
    'and'    : Operator('/and'),
    'or'     : Operator('/or'),
}


def next_token(stream: Stream, skip_space: bool = True) -> Result:
    if skip_space:
        skip_whitespaces(stream)

    char = stream.getch()
    next_char = stream.getch()
    stream.ungetch()

    if char == EOF:
        return Error(['token'], 'EOF')

    elif char == ',':
        return Comma()

    elif char == '(':
        return LParen()

    elif char == ')':
        return RParen()

    elif char.isalpha() or (char == '/' and next_char.isalpha()):
        return tok_identifier(stream, char)

    elif char.isdigit() or char == '.':
        num = char
        char = stream.getch()

        while char.isdigit() or char == '.':
            num += char
            char = stream.getch()

        stream.ungetch()
        if '.' in num:
            try:
                f = float(num)
                return Float(f)
            except (ValueError, OverflowError) as _:
                return Error(['float'], 'parse error')
        else:
            try:
                i = int(num, 10)
                return Integer(i)
            except (ValueError, OverflowError) as _:
                return Error(['int'], 'parse error')

    elif char == '-':
        next_char = stream.getch()
        if next_char == '-':
            # comment, skip until EOL of EOF
            while char != EOF and char != '\n' and char != '\r':
                char = stream.getch()

            return next_token(stream)

        else:
            stream.ungetch()
            return Operator('-')

    elif char == '\'':
        return tok_string(stream)

    # <= /= >=
    elif char in '</>' and next_char == '=':
        stream.getch()  # consume next_char
        return Operator(char + next_char)

    # * / + - < = >
    elif char in ('*', '/', '+', '-', '<', '=', '>'):
        return Operator(char)

    elif char == '?':
        index = next_token(stream, False)
        if not isinstance(index, Integer):
            return Error(['integer'], index.__class__.__name__)
        else:
            return Placeholder(index.value)

    else:
        return Error(['token'], '???')


def tok_identifier(stream: Stream, char: str) -> Token:
    slash = char == '/'
    if slash:
        char = stream.getch()

    ident = ''
    while char.isalnum():
        ident += char
        char = stream.getch()
    stream.ungetch()

    keyword = keywords.get(ident.lower(), None)
    if keyword is not None:
        return keyword

    else:
        return Identifier(ident, slash)


def tok_string(stream: Stream) -> Result:
    string = ''
    char = stream.getch()
    while char != EOF and char != '\'':
        if char == '\\':
            # escape sequence
            char = stream.getch()
        string += char
        char = stream.getch()

    # no ungetch because we want to consume the closing quote

    if char == EOF:
        return Error(['string literal'], 'EOF')
    else:
        return String(string)


def skip_whitespaces(stream: Stream) -> None:
    while True:
        char = stream.getch()
        if char == EOF: break
        if not char.isspace():
            stream.ungetch()
            break

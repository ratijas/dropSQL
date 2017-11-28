from dropSQL.generic import *
from dropSQL.parser.tokens import *

from .stream import Stream


class Tokens(Stream[Token]):
    def __init__(self, characters: Stream[str]) -> None:
        super().__init__()

        self.characters = characters

    def next_impl(self, skip_whitespace: bool = True) -> IResult[Token]:
        print('old current:', self.characters.current())

        self.characters.next()
        if skip_whitespace:
            self.skip_whitespace()

        print('new current:', self.characters.current())

        if self.characters.current().is_err():
            assert self.characters.current().err().is_empty()
            return IErr(Empty())

        char = self.characters.current().ok_or('')
        next_char = self.characters.peek().ok_or('')

        if char == ',':
            return IOk(Comma())

        elif char == '(':
            return IOk(LParen())

        elif char == ')':
            return IOk(RParen())

        elif char.isalpha():
            return IOk(self.parse_identifier())

        elif char == '/' and next_char.isalpha():
            return IOk(self.parse_identifier())

        elif char.isdigit() or char == '.':
            return self.parse_num()

        elif char == '-':
            if next_char == '-':
                # comment, skip until EOL or EOF
                def not_nl(ch: str) -> bool:
                    return not (ch == '\n' or ch == '\r')

                while self.characters.next().map(not_nl).ok_or(False):
                    pass

                return self.next_impl()

            else:
                return IOk(Operator('-'))

        elif char == '\'':
            return self.parse_string()

        # <= /= >=
        elif char in '</>' and next_char == '=':
            self.characters.next()  # consume next_char
            return IOk(Operator(char + next_char))

        # * / + - < = >
        elif char in ('*', '/', '+', '-', '<', '=', '>'):
            return IOk(Operator(char))

        elif char == '?':
            t = self.next_impl(False).and_then(Cast(Integer))
            if not t: return IErr(t.err())

            index = t.ok()
            return IOk(Placeholder(index.value))

        else:
            self.characters.back()
            return IErr(Syntax('token', char))

    # def only_whitespace_left(self) -> bool:
    #         self.skip_whitespace()
    #
    #         # are there any more characters left?
    #         # if so, there are not only whitespaces left.
    #         return not self.characters.peek().is_ok()

    def skip_whitespace(self) -> None:
        """
        Skip whitespace and comments
        """
        while self.characters.current().map(str.isspace).ok_or(False):
            self.characters.next()

    def parse_identifier(self) -> Token:
        assert self.characters.current().ok().isalpha() or (
            self.characters.current().ok() == '/' and self.characters.peek().ok().isalpha())

        slash = (self.characters.current().ok() == '/')
        ident = '' if slash else self.characters.current().ok()

        def is_ident(ch: str) -> bool:
            return ch.isalnum() or ch == '_'

        while self.characters.next().map(is_ident).ok_or(False):
            ident += self.characters.current().ok()

        return Identifier(ident, slash).maybe_as_keyword()

    def parse_string(self) -> IResult[Token]:
        def not_quote(ch: str) -> bool:
            return ch != '\''

        string = ''
        while self.characters.next().map(not_quote).ok_or(False):
            if self.characters.current().ok() == '\\':
                # escape sequence
                self.characters.next()
            string += self.characters.current().ok_or('')

        if self.characters.current().is_err():
            return IErr(Incomplete())
        else:
            return IOk(VarChar(string))

    def parse_num(self) -> IResult[Token]:
        num: str = self.characters.current().ok()

        # @formatter:off
        while (self.characters.peek().is_ok() and
                (self.characters.peek().ok().isdigit() or
                 self.characters.peek().ok() == '.')):
            char = self.characters.next().ok()
            num += char
        # @formatter:on

        if '.' in num:
            try:
                f = float(num)
                return IOk(Float(f))
            except (ValueError, OverflowError) as _:
                return IErr(Syntax('float', num))

        else:
            try:
                i = int(num, 10)
                return IOk(Integer(i))
            except (ValueError, OverflowError) as _:
                return IErr(Syntax('int', num))

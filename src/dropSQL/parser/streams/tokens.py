from dropSQL.generic import *
from dropSQL.parser.tokens import *
from .characters import Characters
from .stream import Stream


class Tokens(Stream[Token]):
    def __init__(self, characters: Stream[str]) -> None:
        super().__init__()

        self.characters = characters

    @classmethod
    def from_str(cls, source: str) -> 'Tokens':
        return Tokens(Characters.from_str(source))

    def next_impl(self, skip_whitespace: bool = True) -> IResult[Token]:
        """
        underlying stream points to current character, token parser uses it.
        """
        # initial condition
        if self.characters.current().is_err() and self.characters.current().err().is_empty():
            self.characters.next()

        if skip_whitespace: self.skip_whitespace()
        if self.characters.current().is_err():
            assert self.characters.current().err().is_empty()
            return IErr(Empty())

        char = self.characters.current().ok()
        next_char = self.characters.peek().ok_or('')
        assert self.characters.current().ok_or('') == char, f'{self.characters.current(), char}'
        assert self.characters.peek().ok_or('') == next_char

        if char == ',':
            self.characters.next()
            return IOk(Comma())

        elif char == '(':
            self.characters.next()
            return IOk(LParen())

        elif char == ')':
            self.characters.next()
            return IOk(RParen())

        elif char.isalpha():
            return IOk(self.parse_identifier())

        elif char == '/' and next_char.isalpha():
            return IOk(self.parse_identifier())

        elif char.isdigit() or char == '.':
            return self.parse_num()

        elif char == '-':
            return self.parse_dash()

        elif char == '\'':
            return self.parse_string()

        # <= /= >=
        elif char in '</>' and next_char == '=':
            self.characters.next()  # consume both
            self.characters.next()
            return IOk(Operator(char + next_char))

        # * / + - < = >
        elif char in ('*', '/', '+', '-', '<', '=', '>'):
            self.characters.next()
            return IOk(Operator(char))

        elif char == '?':
            self.characters.next()
            t = self.next_impl(False).and_then(Cast(Integer))
            if not t: return IErr(t.err())

            index = t.ok()
            return IOk(Placeholder(index.value))

        else:
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
            char = self.characters.current().ok()
            if char == '\\':
                # escape sequence
                char = self.characters.next().ok_or('')
                if char == 'n':
                    char = '\n'
                elif char == 't':
                    char = '\t'
            string += char

        if self.characters.current().is_err():
            return IErr(Incomplete())
        else:
            self.characters.next()
            return IOk(VarChar(string))

    def parse_num(self) -> IResult[Token]:
        num: str = self.characters.current().ok()

        def is_digit(ch: str) -> bool:
            return (ch.isdigit()) or (ch == '.')

        while self.characters.next().map(is_digit).ok_or(False):
            num += self.characters.current().ok()

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

    def parse_dash(self) -> IResult[Token]:
        if self.characters.next().ok_or('') == '-':
            return self.parse_comment()

        else:
            return IOk(Operator('-'))

    def parse_comment(self) -> IResult[Token]:
        # -- comment, skip until EOL or EOF. cursor is at the second dash
        def not_nl(ch: str) -> bool:
            return (ch != '\n') and (ch != '\r')

        while self.characters.next().map(not_nl).ok_or(False): pass
        return self.next_impl()

import abc
from typing import *

from dropSQL.generic import *
from dropSQL.parser.streams import *
from dropSQL.parser.tokens import *
from .ast import Ast
from .expression import *

__all__ = [
    'Ty',
    'IntegerTy',
    'FloatTy',
    'VarCharTy',
]

LiteralTy = TypeVar('LiteralType', ExpressionLiteralInt, ExpressionLiteralFloat, ExpressionLiteralVarChar)


class Ty(Generic[LiteralTy], Ast, metaclass=abc.ABCMeta):
    @classmethod
    def from_sql(cls, tokens: Stream[Token]) -> IResult['Ty']:
        """
        type
            : "integer"
            | "float"
            | "varchar" "(" integer ")"
            ;
        """
        t = tokens.peek().and_then(Cast(Identifier))
        if not t: return IErr(t.err().set_expected('integer, float or varchar type'))

        tok = t.ok()

        if tok == Identifier('integer'):
            tokens.next()
            return Ok(IntegerTy())

        elif tok == Identifier('float'):
            tokens.next()
            return Ok(FloatTy())

        elif tok == Identifier('varchar'):
            t = VarCharTy.from_sql(tokens)
            if not t: return IErr(t.err().empty_to_incomplete())
            return IOk(t.ok())

        else:
            return IErr(Syntax('integer, float or varchar type', str(tok)))

    @abc.abstractmethod
    def construct(self, primitive: PrimitiveTy) -> LiteralTy:
        """
        Construct `Expression` object from the primitive.
        """


class IntegerTy(Ty[ExpressionLiteralInt]):
    def to_sql(self) -> str:
        return 'integer'

    def construct(self, primitive: int) -> ExpressionLiteralInt:
        return ExpressionLiteralInt(primitive)


class FloatTy(Ty[ExpressionLiteralFloat]):
    def to_sql(self) -> str:
        return 'float'

    def construct(self, primitive: float) -> ExpressionLiteralFloat:
        return ExpressionLiteralFloat(primitive)


class VarCharTy(Ty[ExpressionLiteralVarChar]):
    def __init__(self, width: int) -> None:
        super().__init__()

        self.width = width

    def to_sql(self) -> str:
        return f'varchar({self.width})'

    def construct(self, primitive: str) -> ExpressionLiteralVarChar:
        return ExpressionLiteralVarChar(primitive)

    @classmethod
    def from_sql(cls, tokens: Stream[Token]) -> IResult['VarCharTy']:
        """
        varchar
            : "(" integer ")"
            ;
        """

        # next token must be "varchar"
        t = tokens.next().and_then(Cast(Identifier))
        if not t or t.ok() != Identifier('varchar'): return IErr(Syntax('varchar', str(t)))

        t = tokens.next().and_then(Cast(LParen))
        if not t: return IErr(t.err().empty_to_incomplete())

        t = tokens.next().and_then(Cast(Integer))
        if not t: return IErr(t.err().empty_to_incomplete())
        width = t.ok().value

        t = tokens.next().and_then(Cast(RParen))
        if not t: return IErr(t.err().empty_to_incomplete())

        return IOk(VarCharTy(width))

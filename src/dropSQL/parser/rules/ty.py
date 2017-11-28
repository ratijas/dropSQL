from dropSQL.ast import Ty as AstTy, IntegerTy, FloatTy, VarCharTy
from dropSQL.generic import *
from dropSQL.parser.tokens import *
from . import Rule

__all__ = (
    'Ty',
)


class Ty(Rule[AstTy]):
    """
    type
        : "integer"
        | "float"
        | "varchar" "(" integer ")"
        ;
    """

    @classmethod
    def parse(cls, ts: TokenStream) -> Result[AstTy, Expected]:
        t = ts.next().and_then(Cast(Identifier))
        if not t: return Err(t.err().set_expected(['integer', 'float', 'varchar']))

        t = t.ok()

        if t == Identifier('integer'):
            return Ok(IntegerTy())

        elif t == Identifier('float'):
            return Ok(FloatTy())

        elif t == Identifier('varchar'):
            return cls.parse_varchar(ts)

        else:
            return Err(Expected(['type'], str(t)))

    @classmethod
    def parse_varchar(cls, ts: TokenStream) -> Result[VarCharTy, Expected]:
        t = ts.next().and_then(Cast(LParen))
        if not t: return Err(t.err())

        t = ts.next().and_then(Cast(Integer))
        if not t: return Err(t.err())

        width = t.ok().value

        t = ts.next().and_then(Cast(RParen))
        if not t: return Err(t.err())

        return Ok(VarCharTy(width))

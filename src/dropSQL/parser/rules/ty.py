from . import Rule

from dropSQL.parser.expected import Expected
from dropSQL.parser.tokens import *
from dropSQL.generic import *

from dropSQL.ast import Ty as AstTy, IntegerTy, FloatTy, VarCharTy

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
        t = ts.gettok().and_then(caster(Identifier))
        if not t: return Err(Expected(['integer', 'float', 'varchar'], t.err().got))

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
        t = ts.gettok().and_then(caster(LParen))
        if not t: return Err(t.err())

        t = ts.gettok().and_then(caster(Integer))
        if not t: return Err(t.err())

        width = t.ok().value

        t = ts.gettok().and_then(caster(RParen))
        if not t: return Err(t.err())

        return Ok(VarCharTy(width))

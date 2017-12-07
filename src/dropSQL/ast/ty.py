import abc
from typing import *

from dropSQL.engine.types import *
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

INT = b'\0\0'
FLOAT = b'\xff\xff'

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

    ############################
    # methods for `dropSQL.fs` #
    ############################

    @abc.abstractmethod
    def primitive(self) -> 'DB_META_TYPE':
        """
        Return corresponding low-level primitive type.

        Should be used for type-checking values against the table's column type before insertion.
        """

    @abc.abstractmethod
    def struct_format_string(self) -> str:
        """
        Python's `struct` module format string for this type.
        """

    @abc.abstractmethod
    def encode(self) -> bytes:
        """
        Serialize self as 2-bytes type identifier. Used to store column type in the table meta block.

        For Integer and Float magic numbers are b'\0\0' and b'\xff\xff' respectively.
        Any other value denotes width of VarChar type.
        """

    @classmethod
    def decode(cls, magic: bytes) -> 'Ty':
        """
        Deserialize type from 2-bytes type identifier. See `Ty::encode`.
        """
        assert len(magic) == 2

        if magic == INT:
            return IntegerTy()
        elif magic == FLOAT:
            return FloatTy()
        else:
            width = int.from_bytes(magic, byteorder=BYTEORDER)
            return VarCharTy(width)

    @classmethod
    def of(cls, primitive: 'DB_META_TYPE') -> Optional['Ty']:
        if isinstance(primitive, int):
            return IntegerTy()
        elif isinstance(primitive, float):
            return FloatTy()
        elif isinstance(primitive, str):
            return VarCharTy(len(primitive))
        else:
            return None


class IntegerTy(Ty[ExpressionLiteralInt]):
    def to_sql(self) -> str:
        return 'integer'

    def construct(self, primitive: int) -> ExpressionLiteralInt:
        return ExpressionLiteralInt(primitive)

    def primitive(self) -> 'DB_META_TYPE':
        return int

    def struct_format_string(self) -> str:
        return 'i'

    def encode(self) -> bytes:
        assert len(INT) == 2
        return INT


class FloatTy(Ty[ExpressionLiteralFloat]):
    def to_sql(self) -> str:
        return 'float'

    def construct(self, primitive: float) -> ExpressionLiteralFloat:
        return ExpressionLiteralFloat(primitive)

    def primitive(self) -> 'DB_META_TYPE':
        return float

    def struct_format_string(self) -> str:
        return 'f'

    def encode(self) -> bytes:
        assert len(FLOAT) == 2
        return FLOAT


class VarCharTy(Ty[ExpressionLiteralVarChar]):
    def __init__(self, width: int) -> None:
        super().__init__()

        self.width = width

    def to_sql(self) -> str:
        return f'varchar({self.width})'

    def construct(self, primitive: str) -> ExpressionLiteralVarChar:
        return ExpressionLiteralVarChar(primitive)

    def primitive(self) -> 'DB_META_TYPE':
        return str

    def struct_format_string(self) -> str:
        return str(self.width) + 's'

    def encode(self) -> bytes:
        varchar = self.width.to_bytes(2, byteorder=BYTEORDER)
        assert len(varchar) == 2
        return varchar

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

import abc
from typing import *

from dropSQL.ast import Ast
from dropSQL.parser.expected import *
from dropSQL.parser.tokens import TokenStream
from dropSQL.generic import *

T = TypeVar('T', bound=Ast)


class Rule(Generic[T], metaclass=abc.ABCMeta):
    @abc.abstractclassmethod
    def parse(cls, ts: TokenStream) -> Result[T, Expected]:
        ...

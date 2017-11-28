import abc
from typing import *

from dropSQL.ast import Ast
from dropSQL.generic import *
from dropSQL.parser.tokens import TokenStream

T = TypeVar('T', bound=Ast)


class Rule(Generic[T], metaclass=abc.ABCMeta):
    @abc.abstractclassmethod
    def parse(cls, ts: TokenStream) -> Result[T, Expected]:
        ...

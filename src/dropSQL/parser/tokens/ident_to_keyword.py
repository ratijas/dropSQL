from typing import *

from .identifier import Keyword
from . import keywords
from .operator import Operator
from .token import Token

__all__ = ['KEYWORDS']

KEYWORDS: Dict[str, Token] = {}

for kw in keywords.__all__:
    cls = getattr(keywords, kw)
    assert issubclass(cls, Keyword)
    keyword = cls()
    ident = keyword.identifier.lower()
    KEYWORDS[ident] = keyword

KEYWORDS.update({
    'and': Operator('/and'),
    'or' : Operator('/or'),
})

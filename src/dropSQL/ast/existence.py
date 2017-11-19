from . import *

__all__ = (
    'IfExists',
    'IfNotExists',
)


class IfExists(Ast):
    def to_sql(self) -> str:
        return 'if exists'


class IfNotExists(Ast):
    def to_sql(self) -> str:
        return 'if not exists'

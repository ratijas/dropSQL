from .ast import Ast
from .identifier import Identifier
from .ty import Ty


class ColumnDef(Ast):
    def __init__(self, name: Identifier, ty: Ty, is_primary_key: bool) -> None:
        super().__init__()

        self.name = name
        self.ty = ty
        self.is_primary_key = is_primary_key

    def to_sql(self) -> str:
        sql = str(self.name)
        sql += ' '
        sql += self.ty.to_sql()
        if self.is_primary_key:
            sql += ' /primary key'
        sql += ','
        return sql

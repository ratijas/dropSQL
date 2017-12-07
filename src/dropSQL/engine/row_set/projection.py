from typing import *

from dropSQL.parser.tokens import Identifier
from .row_set import RowSet
from ..column import Column
from ..context import Context
from ..row import Row
from ..types import *

if TYPE_CHECKING:
    from dropSQL.ast.result_column import *


class ProjectionRowSet(RowSet):
    def __init__(self, inner: RowSet, columns: List['ResultColumn'], args: ARGS_TYPE) -> None:
        super().__init__()

        self.inner = inner
        self._columns: List[Column] = []
        self.outputs: List['ResultColumn'] = columns
        self.args = args

        for column in columns:
            if column.is_star():
                self._columns.extend(Column(Identifier(''), c.name, c.ty) for c in self.inner.columns())

            else:
                aliased = column.as_expression().expression

                if aliased.alias is not None:
                    alias = aliased.alias
                else:
                    alias = aliased.expression.to_sql()

                # TODO: Expression::derive_type(args) -> Result[Ty]
                from dropSQL.ast.ty import IntegerTy
                ty = IntegerTy()
                self._columns.append(Column(Identifier(''), alias, ty))

        row = next(self.iter(), None)
        if row is not None:
            assert len(row.data) == len(self._columns)
            for column, cell in zip(self._columns, row.data):
                column.ty = column.ty.of(cell)

    def columns(self) -> List[Column]:
        return self._columns

    def iter(self) -> Iterator[Row]:
        ctx = Context.with_args(self.args)
        for row in self.inner.iter():
            ctx.row = row
            data: ROW_TYPE = []

            for out in self.outputs:
                if out.is_star():
                    data.extend(row.data)

                else:
                    expr = out.as_expression().expression.expression
                    res = expr.eval_with(ctx)
                    if not res: raise ValueError(res.err())
                    data.append(res.ok())

            new_row = Row(self, data, row.id)
            yield new_row

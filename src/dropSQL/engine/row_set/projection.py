from typing import *

from dropSQL.ast.result_column import *
from dropSQL.ast.ty import *
from dropSQL.parser.tokens import Identifier
from .row_set import RowSet
from ..column import Column
from ..context import Context
from ..row import Row
from ..types import *

if TYPE_CHECKING:
    pass


class ProjectionRowSet(RowSet):
    def __init__(self, inner: RowSet, columns: List[ResultColumn], args: ARGS_TYPE) -> None:
        super().__init__()

        self.inner = inner
        self._columns: List[Column] = []
        self.outputs: List[ResultColumn] = []

        for column in columns:
            if isinstance(column, ResultStar):
                self._columns.extend(Column(Identifier(''), c.name, c.ty) for c in self.inner.columns())
                self.outputs.append(column)

            elif isinstance(column, ResultExpression):
                aliased = column.expression

                if aliased.alias is not None:
                    alias = aliased.alias
                else:
                    alias = aliased.expression.to_sql()

                # TODO: Expression::derive_type(args) -> Result[Ty]
                ty = IntegerTy()
                self._columns.append(Column(Identifier(''), alias, ty))
                self.outputs.append(column)

        self.args = args

    def columns(self) -> List[Column]:
        return self._columns

    def iter(self) -> Iterator[Row]:
        ctx = Context.with_args(self.args)
        for row in self.inner.iter():
            ctx.row = row
            data: ROW_TYPE = []

            for out in self.outputs:
                if isinstance(out, ResultStar):
                    data.extend(row.data)
                elif isinstance(out, ResultExpression):
                    expr = out.expression.expression
                    res = expr.eval_with(ctx)
                    if not res: raise ValueError(res.err())
                    data.append(res.ok())

            new_row = Row(self, data, row.id)
            yield new_row

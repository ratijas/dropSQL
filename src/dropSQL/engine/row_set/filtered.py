from typing import *

from .row_set import RowSet
from ..column import Column
from ..context import Context
from ..row import Row
from ..types import *

if TYPE_CHECKING:
    from dropSQL.ast.expression import Expression


class FilteredRowSet(RowSet):
    """
    Filters row set based on given predicate expression. Used for `/where`, `/join ... /on` clauses.

    Context
    - row
    - arguments
    - eval(expression: Expression) -> Result[DB_TYPE, error]

    Expression
    - AST
        * references to row's cells
        * references to `?N` arguments
    - eval(context: Context) -> Literal

    Row
    - data: Tuple[DB_TYPE, ...]
    - set: RowSet
    - resolve(reference: ExpressionReference) -> Optional[DB_TYPE]

    For each row in the underlying row set
    """

    def __init__(self, inner: RowSet, expr: 'Expression', args: ARGS_TYPE) -> None:
        super().__init__()

        self.inner = inner
        self.expr = expr
        self.args = args

    def columns(self) -> List[Column]:
        return self.inner.columns()

    def iter(self) -> Iterator[Row]:
        ctx = Context.with_args(self.args)
        for row in self.inner.iter():
            ctx.row = row
            res = self.expr.eval_with(ctx)
            if not res: raise ValueError(res.err())
            if res.ok() != 0:
                yield Row(self, row.data, row.id)

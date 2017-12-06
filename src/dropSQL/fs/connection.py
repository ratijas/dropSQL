from typing import *

from dropSQL.ast.ast import AstStmt
from dropSQL.generic import *
from dropSQL.parser.streams.statements import Statements
from .db_file import DBFile
from dropSQL.engine.types import *


class Connection:
    def __init__(self, path: str = MEMORY) -> None:
        super().__init__()

        self.file = DBFile(path)
        self.cache: Dict[str, AstStmt] = []

    def prepare_statement(self, sql: str) -> IResult[AstStmt]:
        if sql in self.cache:
            stmt = self.cache[sql]
        else:
            # parse and cache a statement
            res = Statements.from_str(sql).collect()
            if not res: return IErr(res.err())

            stmts = res.ok()
            if len(stmts) != 1: return IErr(Syntax('one statement', f'{len(stmts)} statements'))

            stmt = stmts[0]

        return IOk(stmt)

    # TODO
    def execute_statement(self, stmt: AstStmt, args: List[Any] = ()) -> Result[None, None]:
        return stmt.execute(self.file, args)

    def execute(self, sql: str, args: List[Any] = ()) -> Result[None, None]:
        stmt = self.prepare_statement(sql).ok()
        return self.execute_statement(stmt, args)

    def close(self):
        self.file.close()

    def __str__(self) -> str:
        return str(self.file)

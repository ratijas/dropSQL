# noinspection PyUnresolvedReferences
import readline
import sys

from dropSQL import __version__
from dropSQL.engine.row_set.row_set import RowSet
from dropSQL.fs import Connection
from dropSQL.parser.streams.statements import Statements


def open_file_or_memory() -> Connection:
    if len(sys.argv) == 2:
        path = sys.argv[1]
        conn = Connection(path)

    else:
        conn = Connection()

    return conn


class Repl:
    def __init__(self, conn: Connection) -> None:
        super().__init__()

        self.PS1 = '/'
        self.PS2 = '... '

        self.PS = self.PS1
        self.buffer: str = ''

        self.exit = False

        self.conn = conn

    def start(self):
        self.buffer = ''
        self.PS = self.PS1

        while True:
            try:
                line = input(self.PS)
            except KeyboardInterrupt as _:
                print()
                self.reset()
                continue
            except EOFError as _:
                print()
                self.reset()
                break

            self.buffer += line
            self.buffer += '\n'

            for dot in (Help, ListTables):
                if self.buffer.strip() == f'.{dot.name}':
                    dot.execute(self.conn)
                    self.reset()
                    continue

            stmts = Statements.from_str(self.buffer).collect()

            if stmts.is_ok():
                for stmt in stmts.ok():
                    res = self.conn.execute_statement(stmt, [])
                    if not res:
                        print(res)
                        continue

                    r = res.ok()
                    if isinstance(r, RowSet):
                        print(', '.join(str(col.name) for col in r.columns()))
                        for row in enumerate(r.iter()):
                            print(row)
                    else:
                        print(r)
                        # stmt = self.conn.prepare_statement('select * from file where name = ?1').ok()
                        # cursor = stmt.execute(self.conn, ['readme.md'])
                        # for row in cursor:
                        #     print(row)
                        # only one statement

                self.reset()

            elif stmts.err().is_incomplete():
                self.PS = self.PS2

            elif stmts.err().is_syntax():
                print('syntax error:', stmts.err())
                self.reset()

    def reset(self):
        self.buffer = ''
        self.PS = self.PS1


def launch():
    conn = open_file_or_memory()

    print(f'/dropSQL version {__version__}\n'
          f'Enter ".help" for usage hints.\n'
          f'Connected to {conn}')

    Repl(conn).start()
    conn.close()

    print(f'Bye.')


class DotCommand:
    name: str

    @classmethod
    def execute(cls, conn: Connection) -> None:
        return


HELP = """
This is dropSQL REPL. You are connected to {conn}.
Type in commands and watch the output.

.tables     Show all tables in the database.

/create table t(a integer, b float, c varchar(42)) /drop
/drop table if exists t /drop
/insert into t (a, c, b) values (13.37, 42, 'morty'), (.0, 0, '') /drop
/select *, a, 2 * b, c /as d from t Alias /where (c > 100) /and (f /= '') /drop
"""


class Help(DotCommand):
    name = 'help'

    @classmethod
    def execute(cls, conn: Connection) -> None:
        print(HELP.format(conn=conn))


class ListTables(DotCommand):
    name = 'tables'

    @classmethod
    def execute(cls, conn: Connection) -> None:
        print('tables in the database:')
        for i, table in enumerate(conn.file.get_tables()):
            name = table.get_table_name()
            columns = ", ".join(column.to_sql() for column in table.get_columns())
            if name.identifier != '':
                print(f'{i}. {name} ({columns})')

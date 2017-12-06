# noinspection PyUnresolvedReferences
import readline
import sys

from dropSQL import __version__
from dropSQL.engine.row_set import *
from dropSQL.fs import Connection
from dropSQL.parser.streams.statements import Statements
from .formatters import PrettyFormatter


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
                        err = res.err()
                        print('Error:', err, file=sys.stderr)

                    else:
                        r = res.ok()
                        if isinstance(r, RowSet):
                            fmt = PrettyFormatter.with_row_set(r)
                            fmt.format(sys.stdout)

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
                print(stmts.err())
                self.reset()

    def reset(self):
        self.buffer = ''
        self.PS = self.PS1


def launch():
    """
    CLI launcher.
    """
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

.help       Show this help.
.tables     Show all tables in the database.

/create table t(a integer, b float, c varchar(42)) /drop
/insert into t (a, c, b) values (42, 'morty', 13.37), ('', 0, .0) /drop
/select *, a, 2 * b, c /as d from t Alias /where (a < 100) /and (c /= '') /drop
/update t set c = 'rick', a = a + 1 /drop
/delete from t where c > 'r' /drop
/drop   table if exists t /drop
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
        master_table = conn.file.master_table()
        f = PrettyFormatter.with_row_set(master_table)
        f.format(sys.stdout)

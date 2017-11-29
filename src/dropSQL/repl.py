import sys
# noinspection PyUnresolvedReferences
import readline

from dropSQL import __version__
from dropSQL.connection import Connection
from dropSQL.parser.streams.statements import Statements


def open_file_or_memory() -> Connection:
    if len(sys.argv) == 2:
        path = sys.argv[1]
        conn = Connection(path)

    else:
        conn = Connection()

    return conn


class Repl:
    def __init__(self, connection: Connection) -> None:
        super().__init__()

        self.PS1 = '/'
        self.PS2 = '... '

        self.PS = self.PS1
        self.buffer: str = ''

        self.exit = False

        self.connection = connection

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
            stmts = Statements.from_str(self.buffer).collect()

            if stmts.is_ok():
                for stmt in stmts.ok():
                    print(f'parsed rule:', stmt.to_sql())
                    self.connection.execute(stmt)

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

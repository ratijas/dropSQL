import sys

from . import __version__
from .connection import Connection


def open_file_or_memory():
    if len(sys.argv) == 2:
        path = sys.argv[1]
        conn = Connection(path)

    else:
        conn = Connection()

    return conn


def launch():
    conn: Connection = open_file_or_memory()

    print(f'/dropSQL version {__version__}\n'
          'Enter ".help" for usage hints.\n'
          'Connected to {conn}')

    while True:
        try:
            line = input('/')
        except EOFError as e:
            break
        except KeyboardInterrupt as e:
            print()
            continue

        if line == 'retake':
            break
        else:
            conn.execute(line)

    print(f'Bye.')

    conn.close()

# dropSQL

Simple database engine and binary format. Yet another university sucksignment.

# tl;dr

Article on habr.com describing dropSQL internal architecture and design: https://habrahabr.ru/post/347274/

![Article cover](https://hsto.org/webt/rc/0n/pg/rc0npgm2cp9pwpwb6hpcknftmd0.jpeg)

# SQL

dropSQL is a query language, similar to SQL found in modern DBMS implementations. While keywords and identifiers are case-insensitive, most noticeable distinctions are that
- every identifier optionally may start with a slash character (`/`),
- each statement must be followed by '`/drop`' keyword,
- preferred code style for dropSQL is lowercase with slashes as defined in [`parser/tokens/keywords.py`](./src/dropSQL/parser/tokens/keywords.py) file.

Just as SQLite3 does, dropSQL has a master pseudo-table called '/autism'. 'Pseudo' means that it is not regular table, in terms of storage. But it conforms to standard query API, so can be queried as usual. Note that master table can not be modified directly.

dropSQL supports basic CRUD operations:
- Create table with predefined column set.
- Create (insert) rows into tables with values given in a query text.
- Read (select) rows from tables with `/where` clause filter. Implemented joins are:
    * Cross join with comma operator (`,`)
    * Inner join with `a /join b /on condition` syntax
- Update row content.
- Delete row from table.
- Delete (drop) table permanently from a database.

CLI comes with neat multi-line REPL. Start typing a statement like `/create table fruits(`, hit enter, and dropSQL will kindly ask you to proceed with different prompt style (`...` instead of `/`). It will keep reading input until whole statement is typed in. Only then the execution begins, and results are printed back to user.

# Storage

Storage consists of 12KB blocks.
First block contains database name and number of allocated blocks. 
Next 16 blocks contain table descriptors. Table descriptor contains:
- Table name
- Column names and types
- Number of rows in table
- 10 direct pointers to data blocks
- 1 pointer to block of first-level indirect pointers
- 1 pointer to block of second-level indirect pointers
- 1 pointer to block of third-level indirect pointers

Data blocks contain continuous sequence of table records. Each record starts with 'alive'/'removed' mark.

Storage driver allows inserting, deleting, updating and selecting records
by internal ID, as well as creating and dropping tables.

# Roadmap

Things we dream of, but have not implemented yet include:

- Cursor API to use dropSQL from code. For now only CLI is really usable.
- Sub-queries as expressions, like `... /where name = (/select ... from ...) /drop`.
- Unary operators. Even negative numbers have to be writen as `0-N`.
- Type inference for result row set.
- Primary keys and indexes.

# setup.py

## Tests

`$ python3 setup.py test`

## Source distribution

`$ python3 setup.py sdist`

## Installation

`$ python3 setup.py install`

## Running

Executable script should be installed by `setup.py install`:

`$ dropSQL [path/to/database/file]`

Alternatively:

`$ cd path/to/dropSQL/src && python -m dropSQL [path/to/database/file]`

If you don't specify a path to database, by default non-persistent in-memory storage will be used.

# Trivia

Actually, 'drop' is a process of getting the axe by a student, which is usually expressed as a '/drop' slashtag in Telegram group chats.

'/autism' is an another popular phenomena and frequently used slashtag in Innopolis.

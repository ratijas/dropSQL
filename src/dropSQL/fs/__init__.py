"""

File:
    Meta
    [Table; 16]
    [Block]

Meta: Block
    number of total used blocks: i32

Table: Block
    Header
        [Column]  # maximum number of columns depends on columns' content
        table name: str
        row width: int  # >= sum of columns width
        row count: int
        first level blocks: [Pointer[RowData]; 10]
        second level block: Pointer[SecondLevelBlock]
        third level block: Pointer[ThirdLevelBlock]

Column
    name: str
    type: Type

enum Type:
    Integer
    Float
    Varchar(n)

SecondLevelBlock: Block
    [Pointer[RowData]]

ThirdLevelBlock: Block
    [Pointer[SecondLevelBlock]]

RowData: Block
    [Row]  # not quiet

Row
    id: Id
    raw data: [bytes; N]  # N == table->row width

enum Id: i32
    0  # implying row is deleted
    id: i32  # non-zero row id

Pointer[Block]: i32
    # block number in file starting with Meta block at index 0
"""

from typing import *

from dropSQL.generic import *


class OutOfNodes: pass


class Table:
    ...


class Column:
    name: str
    type: Union[float, int, str]

    def __init__(self, name: str) -> None:
        super().__init__()

        self.name = name


class TableDescription:
    def __init__(self, name: str) -> None: ...

    def add_column(self, column: Column) -> Result[None, OutOfNodes]: ...


class File:
    def get_table(self, name: str) -> Result[Table, None]: ...

    def list_tables(self) -> List[Table]: ...

    def new_table(self, description: TableDescription) -> Result[Table, OutOfNodes]: ...


if __name__ == '__main__':
    students = TableDescription('students')

    col = Column('name')
    res = students.add_column(col)
    if res.is_err():
        print(f'can not add column {col.name}')

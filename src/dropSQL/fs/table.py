import struct
from typing import *

from dropSQL.ast.column_def import ColumnDef
from dropSQL.ast.ty import *
from dropSQL.engine.types import *
from dropSQL.generic import *
from dropSQL.parser.tokens import Identifier
from .block import *
from .block_storage import BlockStorage

RAW_TYPE = Union[bytes, int, float]
LVL0 = DIRECT_POINTERS
LVL1 = LVL0 + POINTERS_PER_BLOCK
LVL2 = LVL1 + POINTERS_PER_BLOCK ** 2
LVL3 = LVL2 + POINTERS_PER_BLOCK ** 3

POINTERS_PER_LVL1 = POINTERS_PER_BLOCK
POINTERS_PER_LVL2 = POINTERS_PER_BLOCK ** 2
POINTERS_PER_LVL3 = POINTERS_PER_BLOCK ** 3


class Descriptor:
    """
    Descriptor object holds information about associated table.

    Just as a table can not be created from outside of `DBFile` class,
    `Descriptor` object can only be returned from table's methods.
    Workflow with descriptor:
    >>> table = Table(...)
    >>> d = table.descriptor()
    >>> d.name = Identifier('employer')
    >>> d.save().ok()
    Descriptor object should not be stored apart from table.
    """

    N_POINTERS = DIRECT_POINTERS + 3

    __slots__ = ['table', 'block', 'name', 'pointers', 'records', 'columns']

    def __init__(self, table: 'Table', block: Block, table_name: Identifier, pointers: List[int], records: int,
                 columns: List[ColumnDef]) -> None:
        super().__init__()
        assert len(pointers) == Descriptor.N_POINTERS

        self.table = table
        self.block = block
        self.name = table_name
        self.pointers = pointers
        self.records = records
        self.columns = columns

    @classmethod
    def empty(cls, table: 'Table') -> 'Descriptor':
        return Descriptor(table, Block.empty(1 + table.index), Identifier(''), [0] * Descriptor.N_POINTERS, 0, [])

    @classmethod
    def decode(cls, table: 'Table') -> 'Descriptor':
        try:
            block = table.storage.read_block(1 + table.index)

        except AssertionError:
            return cls.empty(table)

        else:
            base = BLOCK_SIZE - (Descriptor.N_POINTERS * POINTER_SIZE) - POINTER_SIZE

            def get_pointer(b: Block, i: int) -> int:
                return int.from_bytes(b[base + i * POINTER_SIZE:base + (i + 1) * POINTER_SIZE], byteorder=BYTEORDER)

            table_name = Identifier((block.split(b'\0')[0]).decode("UTF-8"), True)
            pointers = [get_pointer(block, i) for i in range(Descriptor.N_POINTERS)]
            records = int.from_bytes(block[BLOCK_SIZE - POINTER_SIZE:], byteorder=BYTEORDER)
            columns: List[ColumnDef] = []

            column_descriptors = block[block.find(b'\0') + 1: base]

            i = 0
            while column_descriptors[i] != 0:
                null = column_descriptors.find(b'\0', i)
                name = column_descriptors[i:null].decode("UTF-8")
                ty = Ty.decode(column_descriptors[null + 1: null + 3])

                columns.append(ColumnDef(Identifier(name), ty, False))  # TODO: primary key
                i = null + 3

            return Descriptor(table, block, table_name, pointers, records, columns)

    def save(self) -> Result[None, str]:
        if self.table.descriptor() is not self: return Err('Descriptor is outdated')

        block = self.block
        i = 0  # insertion pointer

        data = self.name.identifier.encode('UTF-8')
        block.override(i, data + b'\0')
        i += len(data) + 1  # 1 for zero-byte

        for col in self.columns:
            data = col.name.identifier.encode('UTF-8')
            block.override(i, data + b'\0')
            i += len(data) + 1  # 1 for zero-byte

            block.override(i, col.ty.encode())
            i += 2  # column type must be 2 bytes long

        # leave enough room for Descriptor pointers and number of records
        i = BLOCK_SIZE - POINTER_SIZE * (Descriptor.N_POINTERS + 1)

        for pointer in self.pointers:
            block.override(i, pointer.to_bytes(POINTER_SIZE, byteorder=BYTEORDER))
            i += POINTER_SIZE

        block.override(i, self.records.to_bytes(POINTER_SIZE, byteorder=BYTEORDER))

        self.table.storage.write_block(block)
        return Ok(None)


class Table:
    def __init__(self, storage: BlockStorage, index: int) -> None:
        self.storage = storage
        self.index = index
        self._descriptor: Optional[Descriptor] = None

    def descriptor(self) -> Descriptor:
        if self._descriptor is None:
            self._descriptor = Descriptor.decode(self)
        return self._descriptor

    def get_table_name(self) -> Identifier:
        return self.descriptor().name

    def set_table_name(self, new_name: Identifier) -> None:
        descriptor = self.descriptor()
        descriptor.name = new_name
        descriptor.save().ok()

    def get_columns(self) -> List[ColumnDef]:
        return self.descriptor().columns

    def count_records(self) -> int:
        return self.descriptor().records

    # def count_pages(self) -> int:
    #     return self.count_records() * self.record_size // BLOCK_SIZE

    def add_column(self, column: ColumnDef):
        assert self.count_records() == 0, 'Adding column to non-empty table'

        descriptor = self.descriptor()
        descriptor.columns.append(column)
        descriptor.save().ok()

    ###################
    # Page management #
    ###################

    def get_or_allocate_page(self, index: int) -> Block:
        """
        Load or create if necessary a physical block by its page (virtual) index.
        """

        # stage 1: get
        pointer = self._get_page_pointer(index)

        # stage 2: allocate if necessary
        if pointer == 0:
            self._allocate_page(index)
            # repeat
            pointer = self._get_page_pointer(index)

        return self.storage.read_block(pointer)

    def _get_page_pointer(self, index: int) -> int:
        if 0 <= index < LVL0:
            # zero level block
            pointer = self._get_lvl0(index)
        elif LVL0 <= index < LVL1:
            # 1 level block
            pointer = self._get_lvl1(index)
        elif LVL1 <= index < LVL2:
            # 2 level block
            pointer = self._get_lvl2(index)
        elif LVL2 <= index < LVL3:
            # 3 level block
            pointer = self._get_lvl3(index)
        else:
            # invalid / overflow
            pointer = 0

        return pointer

    def _allocate_page(self, index: int) -> None:
        assert self._get_page_pointer(index) == 0

        if 0 <= index < LVL0:
            # zero level block
            self._allocate_lvl0(index)
        elif LVL0 <= index < LVL1:
            # 1 level block
            self._allocate_lvl1(index)
        elif LVL1 <= index < LVL2:
            # 2 level block
            self._allocate_lvl2(index)
        elif LVL2 <= index < LVL3:
            # 3 level block
            self._allocate_lvl3(index)

    def _allocate_lvl0(self, index: int) -> None:
        assert 0 <= index < LVL0
        assert 0 == self._get_lvl0(index)

        lvl0 = self.storage.allocate_block().idx

        descriptor = self.descriptor()
        descriptor.pointers[index] = lvl0
        descriptor.save().ok()

    def _allocate_lvl1(self, index: int) -> None:
        assert LVL0 <= index < LVL1
        assert 0 == self._get_lvl1(index)
        index -= LVL0
        descriptor = self.descriptor()

        lvl1 = descriptor.pointers[DIRECT_POINTERS]  # next after direct pointers
        if lvl1 == 0:
            lvl1 = self.storage.allocate_block().idx
            descriptor.pointers[DIRECT_POINTERS] = lvl1
            descriptor.save()

        self._allocate_last_mile(lvl1, index)

    def _allocate_lvl2(self, index: int) -> None:
        assert LVL1 <= index < LVL2
        assert 0 == self._get_lvl2(index)
        index -= LVL1
        descriptor = self.descriptor()

        lvl2 = descriptor.pointers[DIRECT_POINTERS + 1]  # second after direct pointers
        if lvl2 == 0:
            lvl2 = self.storage.allocate_block().idx
            descriptor.pointers[DIRECT_POINTERS + 1] = lvl2
            descriptor.save()

        block = self.storage.read_block(lvl2)
        lvl1 = block.get_pointer(index // POINTERS_PER_LVL1)
        if lvl1 == 0:
            lvl1 = self.storage.allocate_block().idx
            block.set_pointer(index // POINTERS_PER_LVL1, lvl1)
            self.storage.write_block(block)

        self._allocate_last_mile(lvl1, index)

    def _allocate_lvl3(self, index: int) -> None:
        assert LVL2 <= index < LVL3
        assert 0 == self._get_lvl3(index)
        index -= LVL2
        descriptor = self.descriptor()

        lvl3 = descriptor.pointers[DIRECT_POINTERS + 2]  # second after direct pointers
        if lvl3 == 0:
            lvl3 = self.storage.allocate_block().idx
            descriptor.pointers[DIRECT_POINTERS + 2] = lvl3
            descriptor.save()

        block = self.storage.read_block(lvl3)
        lvl2 = block.get_pointer(index // POINTERS_PER_LVL2)
        if lvl2 == 0:
            lvl2 = self.storage.allocate_block().idx
            block.set_pointer(index // POINTERS_PER_LVL2, lvl2)
            self.storage.write_block(block)

        block = self.storage.read_block(lvl2)
        lvl1 = block.get_pointer(index // POINTERS_PER_LVL1)
        if lvl1 == 0:
            lvl1 = self.storage.allocate_block().idx
            block.set_pointer(index // POINTERS_PER_LVL1, lvl1)
            self.storage.write_block(block)

        self._allocate_last_mile(lvl1, index)

    def _allocate_last_mile(self, pointer: int, index: int) -> None:
        lvl0 = self.storage.allocate_block().idx
        block = self.storage.read_block(pointer)
        block.set_pointer(index % POINTERS_PER_LVL1, lvl0)
        self.storage.write_block(block)

    def _get_lvl0(self, index: int) -> int:
        assert 0 <= index < LVL0

        lvl0 = self.descriptor().pointers[index]
        return lvl0

    def _get_lvl1(self, index: int) -> int:
        assert LVL0 <= index < LVL1
        index -= LVL0

        lvl1 = self.descriptor().pointers[DIRECT_POINTERS]  # next after direct pointers
        if lvl1 == 0: return 0
        block = self.storage.read_block(lvl1)

        lvl0 = block.get_pointer(index)
        return lvl0

    def _get_lvl2(self, index: int) -> int:
        assert LVL1 <= index < LVL2
        index -= LVL1

        lvl2 = self.descriptor().pointers[DIRECT_POINTERS + 1]  # second after direct pointers
        if lvl2 == 0: return 0
        block = self.storage.read_block(lvl2)

        lvl1 = block.get_pointer(index // POINTERS_PER_LVL1)
        if lvl1 == 0: return 0
        block = self.storage.read_block(lvl1)

        lvl0 = block.get_pointer(index % POINTERS_PER_LVL1)
        return lvl0

    def _get_lvl3(self, index: int) -> int:
        assert LVL2 <= index < LVL3
        index -= LVL2

        lvl3 = self.descriptor().pointers[DIRECT_POINTERS + 2]  # third after direct pointers
        if lvl3 == 0: return 0
        block = self.storage.read_block(lvl3)

        lvl2 = block.get_pointer(index // POINTERS_PER_LVL2)
        if lvl2 == 0: return 0
        block = self.storage.read_block(lvl2)

        lvl1 = block.get_pointer(index // POINTERS_PER_LVL1)
        if lvl1 == 0: return 0
        block = self.storage.read_block(lvl1)

        lvl0 = block.get_pointer(index % POINTERS_PER_LVL1)
        return lvl0

    ##################
    # CRUD Internals #
    ##################

    def _increment_record_counter(self) -> int:
        """
        :return: old record counter
        """
        descriptor = self.descriptor()
        rc = descriptor.records
        descriptor.records += 1
        descriptor.save().ok()
        return rc

    def page_and_offset(self, record: int) -> (int, int):
        record_offset = self.record_size * record
        page = record_offset // BLOCK_SIZE
        offset = record_offset % BLOCK_SIZE

        return page, offset

    def _read_record(self, index: int) -> bytes:
        page, offset = self.page_and_offset(index)

        return self._read(page, offset, self.record_size)

    def _read(self, page: int, offset: int, n: int) -> bytes:
        """ Read n bytes from the page(s) starting from given page (virtual index) with given offset.

        Record may cross page boundary.
        """
        record = bytearray()

        # first page

        block = self.get_or_allocate_page(page)
        chunk = block[offset:min(offset + n, BLOCK_SIZE)]
        record.extend(chunk)

        # full pages

        first = len(chunk)
        i = 1
        while first + (i + 1) * BLOCK_SIZE <= n:
            block = self.get_or_allocate_page(page + i)
            record.extend(block)
            i += 1

        # last, beginning of the page

        if len(record) < n:
            block = self.get_or_allocate_page(page + i)
            chunk = block[:n - len(record)]
            record.extend(chunk)

        assert len(record) == n

        return bytes(record)

    def _write_record(self, record: bytes, index: int) -> None:
        page, offset = self.page_and_offset(index)

        self._write(page, offset, record)

    def _write(self, page: int, offset: int, record: bytes) -> None:
        """ Write down record (bytes) onto the page (virtual index) starting with given offset.

        Record may cross page boundary.
        """

        # first page

        chunk = record[:BLOCK_SIZE - offset]
        block = self.get_or_allocate_page(page)
        block.override(offset, chunk)
        self.storage.write_block(block)

        # full pages

        i = 1
        while (i + 1) * BLOCK_SIZE - offset <= len(record):
            chunk = record[i * BLOCK_SIZE - offset:(i + 1) * BLOCK_SIZE - offset]
            block = self.get_or_allocate_page(page + i)
            block.override(0, chunk)
            self.storage.write_block(block)
            i += 1

        # last, beginning of the page

        chunk = record[i * BLOCK_SIZE - offset:]
        if chunk:
            block = self.get_or_allocate_page(page + i)
            block.override(0, chunk)
            self.storage.write_block(block)

    ########
    # CRUD #
    ########

    def insert(self, values: ROW_TYPE, record_num: int = -1) -> Result[int, str]:
        """
        :return: Ok(record id) or Err(error description)
        """
        res = self._validate_insert_values(values)
        if not res: return Err(res.err())
        record = self._encode_record(values)

        if record_num > self.count_records():
            return Err('record_num({}) > #records({})'.format(record_num, self.count_records()))

        if record_num == -1: record_num = self._increment_record_counter()

        self._write_record(record, record_num)

        return Ok(record_num)

    def select(self, record_num: int) -> Result[ROW_TYPE, str]:
        if record_num >= self.count_records():
            return Err('record_num({}) >= #records({})'.format(record_num, self.count_records()))

        binary = self._read_record(record_num)

        res = self._decode_record(binary)
        if not res: return Err(res.err())
        row = res.ok()

        return Ok(row)

    def delete(self, record_num: int) -> Result[None, str]:
        if record_num >= self.count_records():
            return Err('record_num({}) >= #records({})'.format(record_num, self.count_records()))

        page, offset = self.page_and_offset(record_num)

        self._write(page, offset, b'd')

        return Ok(None)

    def update(self, values: ROW_TYPE, index: int) -> Result[int, str]:
        return self.insert(values, index)

    def drop(self) -> None:
        self._descriptor = Descriptor.empty(self)
        self._descriptor.save().ok()

    #############
    # Internals #
    #############

    def _validate_insert_values(self, values: ROW_TYPE) -> Result[None, str]:
        """
        Ensure all columns of this table are present
        """
        columns = self.get_columns()

        if len(values) != len(columns):
            return Err(f'number of values ({len(values)} != number of columns ({len(columns)})')

        for i, (column, value) in enumerate(zip(columns, values)):
            ty = column.ty.primitive()
            if not isinstance(value, ty):
                return Err(f'value #{i} has type {type(value).__name__}, expected: {ty.__name__}')

        return Ok(None)

    def _calculate_record_size(self) -> int:
        return struct.calcsize(self._struct_format_string())

    @property
    def record_size(self) -> int:
        return self._calculate_record_size()

    def _struct_format_string(self) -> str:
        fmt = 'c' + ''.join(column.ty.struct_format_string()
                            for column in self.get_columns())
        return fmt

    def _decode_record(self, binary: bytes) -> Result[ROW_TYPE, str]:
        try:
            data = struct.unpack(self._struct_format_string(), binary)
        except struct.error as e:
            return Err(str(e))

        if data[0] == b'd': return Err('Record is dead')
        if data[0] != b'a': return Err('Incorrect record: {}'.format(data))

        if len(data) - 1 != len(self.get_columns()):
            return Err('record({}) != #columns({})'.format(len(data) - 1, len(self.get_columns())))

        r = bytes_to_str(list(data[1:]))
        if not r: return Err(r.err())
        return Ok(r.ok())

    def _encode_record(self, values: ROW_TYPE):
        """
        Assume that value types correspond to column types.
        """
        t: List[RAW_TYPE] = [b'a']  # alive FIXME
        for v in values:
            if isinstance(v, str):
                t.append(v.encode("UTF-8"))
            else:
                t.append(v)
        return struct.pack(self._struct_format_string(), *t)


def bytes_to_str(row: ROW_TYPE) -> Result[ROW_TYPE, str]:
    """ Convert bytes back to utf-8 str. """
    for i in range(len(row)):
        value = row[i]
        if isinstance(value, bytes):
            try:
                row[i] = value.split(b'\0')[0].decode("UTF-8")
            except UnicodeDecodeError as e:
                return Err(str(e))
    return Ok(row)

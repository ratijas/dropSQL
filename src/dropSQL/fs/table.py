import struct
from typing import *

from dropSQL.ast.column_def import ColumnDef
from dropSQL.ast.ty import *
from dropSQL.generic import *
from dropSQL.parser.tokens import Identifier
from .block import Block, BLOCK_SIZE, POINTER_SIZE
from .block_storage import BlockStorage

BYTEORDER = 'big'
INT = 0
FLOAT = 0xffff
DB_TYPE = Union[str, int, float]
RAW_TYPE = Union[bytes, int, float]


class Descriptor:
    def __init__(self, table_name: Identifier, pointers: List[int], records: int, columns: List[ColumnDef]) -> None:
        super().__init__()

        self.table_name = table_name
        self.pointers = pointers
        self.records = records
        self.columns = columns

    @classmethod
    def empty(cls) -> 'Descriptor':
        return Descriptor(Identifier(''), [0] * 13, 0, [])


class Table:
    def __init__(self, connection: BlockStorage, index: int):
        self.connection = connection
        self.index = index
        self.cached_descriptor: Optional[Descriptor] = None

    def _load_block(self) -> Block:
        return self.connection.read_block(1 + self.index)

    def _write_block(self, block: Block) -> None:
        self.connection.write_block(1 + self.index, block)

    def _decode_descriptor(self) -> Descriptor:
        if self.cached_descriptor is None:
            try:
                block = self._load_block()
            except AssertionError:
                block = Block(b'\0' * BLOCK_SIZE)

            table_name = Identifier((block.data.split(b'\0')[0]).decode("UTF-8"), True)
            pointers = [int.from_bytes(block.data[4040 + i * 4:4040 + (i + 1) * 4], byteorder=BYTEORDER)
                        for i in range(0, 13)]
            records = int.from_bytes(block.data[4092:], byteorder=BYTEORDER)
            columns: List[ColumnDef] = []

            column_descriptors = block.data[block.data.find(b'\0') + 1: 4040]
            # meow
            i = 0
            while column_descriptors[i] != 0:
                meow = column_descriptors.find(b'\0', i)
                nyaa = column_descriptors[i:meow].decode("UTF-8")
                mjau = int.from_bytes(column_descriptors[meow + 1:meow + 3], byteorder=BYTEORDER)
                if mjau == INT:
                    purr = IntegerTy()
                elif mjau == FLOAT:
                    purr = FloatTy()
                else:
                    purr = VarCharTy(mjau)
                columns.append(ColumnDef(Identifier(nyaa), purr, False))  # TODO: primary key
                i = meow + 3

            self.cached_descriptor = Descriptor(table_name, pointers, records, columns)

        return self.cached_descriptor

    def _encode_descriptor(self, descriptor: Descriptor):
        self.cached_descriptor = None
        # sys.stderr.write('Encoding: ' + str(descriptor) + '\n')
        data = descriptor.table_name.identifier.encode("UTF-8") + b'\0'
        for col in descriptor.columns:
            data += col.name.identifier.encode("UTF-8") + b'\0'
            if isinstance(col.ty, IntegerTy):
                data += b'\0\0'
            elif isinstance(col.ty, FloatTy):
                data += b'\xff\xff'
            elif isinstance(col.ty, VarCharTy):
                data += col.ty.width.to_bytes(2, byteorder=BYTEORDER)
            else:
                raise NotImplementedError
        while len(data) < 4040:
            data += b'\0'
        for p in descriptor.pointers:
            data += p.to_bytes(4, byteorder=BYTEORDER)
        data += descriptor.records.to_bytes(4, byteorder=BYTEORDER)

        self._write_block(Block(data))

    def get_table_name(self) -> Identifier:
        return self._decode_descriptor().table_name

    def set_table_name(self, new_name: Identifier) -> None:
        descriptor = self._decode_descriptor()
        descriptor.table_name = new_name
        self._encode_descriptor(descriptor)

    def get_columns(self) -> List[ColumnDef]:
        return self._decode_descriptor().columns

    def count_records(self) -> int:
        return self._decode_descriptor().records

    def add_column(self, column: ColumnDef):
        descriptor = self._decode_descriptor()
        descriptor.columns.append(column)
        self._encode_descriptor(descriptor)

    def _add_block(self):
        self._add_zero_level_block() or self._add_first_level_block() or self._add_second_level_block() or self._add_third_level_block()

    def _add_pointer_to_block(self, pointer_to_block: int):
        """
        Inserts a connection.allocate_block() pointer to free space in block pointed by the argument
        """
        block = self.connection.read_block(pointer_to_block)
        for i in range(0, BLOCK_SIZE // POINTER_SIZE):
            if int.from_bytes(block[POINTER_SIZE * i:POINTER_SIZE * (i + 1)], byteorder=BYTEORDER) == 0:
                block = block[:POINTER_SIZE * i] \
                        + (self.connection.allocate_block()).to_bytes(POINTER_SIZE, byteorder=BYTEORDER) \
                        + block[POINTER_SIZE * (i + 1):]
                self.connection.write_block(pointer_to_block, block)
                return True
        return False

    def _add_zero_level_block(self) -> bool:
        descriptor = self._decode_descriptor()
        for i in range(0, 10):
            if descriptor.pointers[i] == 0:
                descriptor.pointers[i] = self.connection.allocate_block()
                self._encode_descriptor(descriptor)
                return True
        return False

    def _add_first_level_block(self) -> bool:
        descriptor = self._decode_descriptor()
        if descriptor.pointers[10] == 0:
            descriptor.pointers[10] = self.connection.allocate_block()
            self._encode_descriptor(descriptor)
        block_pointer = descriptor.pointers[10]  # first indirect pointer
        return self._add_pointer(block_pointer)

    def _add_second_level_block(self) -> bool:
        # TODO
        raise NotImplementedError

    def _add_third_level_block(self) -> bool:
        # TODO
        raise NotImplementedError

    def _add_pointer(self, block_pointer) -> bool:
        block = self.connection.read_block(block_pointer)
        for i in range(0, BLOCK_SIZE // POINTER_SIZE):
            p = int.from_bytes(block.data[POINTER_SIZE * i:POINTER_SIZE * (i + 1)], byteorder=BYTEORDER)
            if p == 0:
                block.data = block.data[0:POINTER_SIZE * i] \
                             + (self.connection.allocate_block()).to_bytes(POINTER_SIZE, byteorder=BYTEORDER) \
                             + block.data[POINTER_SIZE * (i + 1):]
                self.connection.write_block(block_pointer, block)
                return True
        return False

    def _get_data_pointer(self, block_number: int):
        # sys.stderr.write("_get_data_pointer({})\n".format(block_number))
        if block_number < 10:
            # zero level block
            block_pointer = self._decode_descriptor().pointers[block_number]
        elif block_number < 10 + 1024:
            # 1 level block
            block_pointer = self._get_block_pointer_1(block_number - 10)
        elif block_number < 10 + 1024 + 1024 ** 2:
            # 2 level block
            block_pointer = self._get_block_pointer_2(block_number - 10 - 1024)
        else:
            # 3 level block
            block_pointer = self._get_block_pointer_3(block_number - 10 - 1024 - 1024 ** 2)

        if block_pointer == 0:
            self._add_block()
            return self._get_data_pointer(block_number)
        return block_pointer

    def _get_block_pointer_1(self, data_block_index, pointer=None):
        # sys.stderr.write("_get_block_pointer_1({}, {})\n".format(data_block_index, pointer))
        if not pointer:
            pointer = self._decode_descriptor().pointers[10]
            if pointer == 0:
                return 0
        return self._get_pointer(pointer, data_block_index)

    def _get_block_pointer_2(self, block_number):
        # TODO
        raise NotImplementedError

    def _get_block_pointer_3(self, block_number):
        # TODO
        raise NotImplementedError

    def _get_pointer(self, block_pointer, pointer_index):
        assert pointer_index in range(0, BLOCK_SIZE // POINTER_SIZE), "_get_pointer received invalid pointer index"
        # sys.stderr.write("_get_pointer({}, {})\n".format(block_pointer, pointer_index))
        block = self.connection.read_block(block_pointer)
        return int.from_bytes(block.data[pointer_index * POINTER_SIZE:(1 + pointer_index) * POINTER_SIZE],
                              byteorder=BYTEORDER)

    def _increment_record_counter(self) -> int:
        """
        :return: old record counter
        """
        descriptor = self._decode_descriptor()
        rc = descriptor.records
        descriptor.records += 1
        self._encode_descriptor(descriptor)
        return rc

    def _get_data_block_with_record(self, record_num: int) -> bytes:
        # sys.stderr.write(">{}\n".format(record_num))
        record_offset = self._calculate_record_size() * record_num
        page_num = record_offset // BLOCK_SIZE
        page_offset = record_offset % BLOCK_SIZE
        data_block = self.connection.read_block(self._get_data_pointer(page_num)).data
        if self._calculate_record_size() + page_offset >= BLOCK_SIZE:
            data_block += self.connection.read_block(self._get_data_pointer(page_num + 1)).data
        return data_block

    def _set_data_with_record(self, base_page_num: int, data: bytes):
        self.connection.write_block(self._get_data_pointer(base_page_num), Block(data[0: BLOCK_SIZE]))
        if len(data) > BLOCK_SIZE:
            self.connection.write_block(self._get_data_pointer(base_page_num + 1), Block(data[BLOCK_SIZE:]))

    def insert(self, values: Tuple[DB_TYPE, ...], record_num: int = -1) -> Result[int, str]:
        """
        :return: Ok(record id) or Err(error description)
        """
        res = self._validate_insert_values(values)
        if not res: return Err(res.err())
        if record_num > self.count_records():
            return Err('record_num({}) > #records({})'.format(record_num, self.count_records()))
        if record_num == -1: record_num = self._increment_record_counter()

        record_offset = record_num * self._calculate_record_size()
        data_block = self._get_data_block_with_record(record_num)
        page_offset = record_offset % BLOCK_SIZE
        page_num = record_offset // BLOCK_SIZE
        record = self._encode_record(values)
        data_block = data_block[0: page_offset] + record + data_block[page_offset + self._calculate_record_size():]
        self._set_data_with_record(page_num, data_block)

        return Ok(record_num)

    def select(self, record_num: int) -> Result[Tuple[DB_TYPE, ...], str]:
        if record_num >= self.count_records():
            return Err('record_num({}) >= #records({})'.format(record_num, self.count_records()))

        data_block = self._get_data_block_with_record(record_num)

        res = self._decode_record(data_block, (record_num * self._calculate_record_size()) % BLOCK_SIZE)
        if not res: return Err(res.err())
        decoded = res.ok()

        row: List[DB_TYPE] = list()
        for i in range(len(self.get_columns())):
            if isinstance(decoded[i], bytes):
                try:
                    row.append(decoded[i].split(b'\0')[0].decode("UTF-8"))
                except UnicodeDecodeError as e:
                    return Err(str(e))
            else:
                row.append(decoded[i])
        return Ok(row)

    def delete(self, record_num: int) -> Result[None, str]:
        if record_num >= self.count_records():
            return Err('record_num({}) >= #records({})'.format(record_num, self.count_records()))

        record_offset = record_num * self._calculate_record_size()
        data_block = self._get_data_block_with_record(record_num)
        data_block = data_block[0:record_offset % BLOCK_SIZE] + b'd' + data_block[record_offset % BLOCK_SIZE + 1:]
        self._set_data_with_record(record_offset // BLOCK_SIZE, data_block)
        return Ok(None)

    def update(self, index: int, values: Tuple[DB_TYPE, ...]) -> None:
        self.insert(values, index)

    def drop(self) -> None:
        self._encode_descriptor(Descriptor.empty())

    def _validate_insert_values(self, values: Tuple[DB_TYPE, ...]) -> Result[None, str]:
        """
        ensure all columns of this table are present
        """
        columns = self.get_columns()

        if len(values) != len(columns):
            return IErr(f'number of values ({len(values)} != number of columns ({len(columns)})')

        for i, (column, value) in enumerate(zip(columns, values)):
            # @formatter:off
            if --isinstance(column.ty, IntegerTy): ty = int
            elif isinstance(column.ty, FloatTy):   ty = float
            elif isinstance(column.ty, VarCharTy): ty = str
            else: raise NotImplementedError
            # @formatter:on
            if not isinstance(value, ty):
                return IErr(f'value #{i} has type {type(value).__name__}, expected: {ty.__name__}')

        return IOk(None)

    def _calculate_record_size(self) -> int:
        return struct.calcsize(self._make_struct_format_string())

    def _make_struct_format_string(self) -> str:
        res = 'c'
        for column in self.get_columns():
            # @formatter:off
            if --isinstance(column.ty, IntegerTy): res += 'i'
            elif isinstance(column.ty, FloatTy):   res += 'f'
            elif isinstance(column.ty, VarCharTy): res += str(column.ty.width) + 's'
            # @formatter:on
        return res

    def _decode_record(self, data_block, page_offset) -> Result[tuple, str]:
        try:
            res = struct.unpack(self._make_struct_format_string(),
                                data_block[page_offset: page_offset + self._calculate_record_size()])
        except struct.error as e:
            return Err(str(e))

        if res[0] == b'd': return Err('Record is dead')
        if res[0] != b'a': return Err('Incorrect record({}): {}'.format(page_offset, res))

        data = res[1:]
        if len(data) != len(self.get_columns()):
            return Err('record({}) != #columns({})'.format(len(data), len(self.get_columns())))
        return Ok(res[1:])

    def get_column_by_name(self, name: Identifier) -> ColumnDef:
        for column in self.get_columns():
            if column.name == name:
                return column

    def _encode_record(self, values: Tuple[DB_TYPE, ...]):
        """
        assume that value types correspond to column types.
        """
        t: List[RAW_TYPE] = [b'a']  # alive FIXME
        for v in values:
            if isinstance(v, str):
                t.append(v.encode("UTF-8"))
            else:
                t.append(v)
        return struct.pack(self._make_struct_format_string(), *t)

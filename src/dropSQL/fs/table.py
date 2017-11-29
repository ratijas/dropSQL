import struct
from typing import *

from dropSQL.ast.column_def import ColumnDef
from dropSQL.ast.ty import *
from dropSQL.parser.tokens import Identifier, Literal, VarChar
from .block import Block, BLOCK_SIZE, POINTER_SIZE
from .block_storage import BlockStorage


class Table:
    def __init__(self, connection: BlockStorage, index: int):
        self.connection = connection
        self.index = index
        self.cached_descriptor = None

    def _load_block(self) -> Block:
        return self.connection.read_block(1 + self.index)

    def _write_block(self, block: Block) -> None:
        self.connection.write_block(1 + self.index, block)

    def _decode_descriptor(self) -> dict:
        if self.cached_descriptor:
            return self.cached_descriptor

        else:
            try:
                block = self._load_block()
            except AssertionError:
                block = Block(b'\0' * BLOCK_SIZE)

            table_descriptor = {
                "table_name": (block.data.split(b'\0')[0]).decode("UTF-8"),
                "pointers"  : [int.from_bytes(block.data[4040 + i * 4:4040 + (i + 1) * 4], byteorder='big')
                               for i in range(0, 13)],
                "records"   : int.from_bytes(block.data[4092:], byteorder='big')
            }

            columns: List[ColumnDef] = []
            column_descriptors = block.data[block.data.find(b'\0') + 1: 4040]
            # meow
            i = 0
            while True:
                if column_descriptors[i] == 0:
                    break
                else:
                    meow = column_descriptors.find(b'\0', i)
                    nyaa = column_descriptors[i:meow].decode("UTF-8")
                    mjau = int.from_bytes(column_descriptors[meow + 1:meow + 3], byteorder='big')
                    if mjau == 0:
                        purr = IntegerTy()
                    else:
                        if mjau == 0xffff:
                            purr = FloatTy()
                        else:
                            purr = VarCharTy(mjau)
                    columns.append(ColumnDef(Identifier(nyaa), purr, False))
                    i = meow + 3

        table_descriptor["columns"] = columns
        self.cached_descriptor = table_descriptor
        return table_descriptor

    def _encode_descriptor(self, descriptor: dict):
        self.cached_descriptor = None
        # sys.stderr.write('Encoding: ' + str(descriptor) + '\n')
        data = descriptor["table_name"].encode("UTF-8") + b'\0'
        for col in descriptor["columns"]:
            col: ColumnDef = col
            data += col.name.identifier.encode("UTF-8") + b'\0'
            if isinstance(col.ty, IntegerTy):
                data += b'\0\0'
            elif isinstance(col.ty, FloatTy):
                data += b'\xff\xff'
            elif isinstance(col.ty, VarCharTy):
                data += col.ty.width.to_bytes(2, byteorder='big')
            else:
                raise NotImplementedError
        while len(data) < 4040:
            data += b'\0'
        for p in descriptor["pointers"]:
            data += p.to_bytes(4, byteorder='big')
        data += descriptor["records"].to_bytes(4, byteorder='big')

        self._write_block(Block(data))

    def get_table_name(self) -> Identifier:
        return Identifier(self._decode_descriptor()["table_name"], True)

    def set_table_name(self, new_name: Identifier) -> None:
        descriptor = self._decode_descriptor()
        descriptor["table_name"] = new_name.identifier.lower()
        self._encode_descriptor(descriptor)

    def get_columns(self) -> List[ColumnDef]:
        return self._decode_descriptor()["columns"]

    def count_records(self) -> int:
        return self._decode_descriptor()["records"]

    def add_column(self, column: ColumnDef):
        descriptor = self._decode_descriptor()
        descriptor["columns"].append(column)
        self._encode_descriptor(descriptor)

    def _add_block(self):
        self._add_zero_level_block() or self._add_first_level_block() or self._add_second_level_block() or self._add_third_level_block()

    def _add_pointer_to_block(self, pointer_to_block: int):
        """
        Inserts a connection.allocate_block() pointer to free space in block pointed by the argument
        """
        block = self.connection.read_block(pointer_to_block)
        for i in range(0, BLOCK_SIZE // POINTER_SIZE):
            if int.from_bytes(block[POINTER_SIZE * i:POINTER_SIZE * (i + 1)], byteorder='big') == 0:
                block = block[:POINTER_SIZE * i] \
                        + (self.connection.allocate_block()).to_bytes(POINTER_SIZE, byteorder='big') \
                        + block[POINTER_SIZE * (i + 1):]
                self.connection.write_block(pointer_to_block, block)
                return True
        return False

    def _add_zero_level_block(self) -> bool:
        descriptor = self._decode_descriptor()
        for i in range(0, 10):
            if descriptor["pointers"][i] == 0:
                descriptor["pointers"][i] = self.connection.allocate_block()
                self._encode_descriptor(descriptor)
                return True
        return False

    def _add_first_level_block(self) -> bool:
        descriptor = self._decode_descriptor()
        if descriptor["pointers"][10] == 0:
            descriptor["pointers"][10] = self.connection.allocate_block()
            self._encode_descriptor(descriptor)
        block_pointer = descriptor["pointers"][10]  # first indirect pointer
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
            p = int.from_bytes(block.data[POINTER_SIZE * i:POINTER_SIZE * (i + 1)], byteorder='big')
            if p == 0:
                block.data = block.data[0:POINTER_SIZE * i] \
                             + (self.connection.allocate_block()).to_bytes(POINTER_SIZE, byteorder='big') \
                             + block.data[POINTER_SIZE * (i + 1):]
                self.connection.write_block(block_pointer, block)
                return True
        return False

    def _get_data_pointer(self, block_number: int):
        # sys.stderr.write("_get_data_pointer({})\n".format(block_number))
        if block_number < 10:
            # zero level block
            block_pointer = self._decode_descriptor()["pointers"][block_number]
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
            pointer = self._decode_descriptor()["pointers"][10]
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
                              byteorder='big')

    def _increment_record_counter(self):
        descriptor = self._decode_descriptor()
        descriptor["records"] = descriptor["records"] + 1
        self._encode_descriptor(descriptor)

    def _get_data_block_with_record(self, record_num: int) -> Block:
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

    def insert(self, values: Dict[Identifier, Literal], record_num=-1):
        self._validate_insert_values(values)
        if record_num == -1:
            record_num = self.count_records()
            self._increment_record_counter()
        record_offset = record_num * self._calculate_record_size()
        data_block = self._get_data_block_with_record(record_num)
        page_offset = record_offset % BLOCK_SIZE
        page_num = record_offset // BLOCK_SIZE
        record = self._encode_record(values)
        data_block = data_block[0: page_offset] + record + data_block[page_offset + self._calculate_record_size():]
        self._set_data_with_record(page_num, data_block)

    def select(self, record_num: int):
        assert record_num < self.count_records(), \
            "Record num is bigger than number of records in the table: {}, {}" \
                .format(record_num, self.count_records())
        data_block = self._get_data_block_with_record(record_num)
        decoded = self._decode_record(data_block, (record_num * self._calculate_record_size()) % BLOCK_SIZE)
        fixed = list()
        for i in range(0, len(self.get_columns())):
            if type(decoded[i]) == bytes:
                fixed.append(decoded[i].split(b'\0')[0].decode("UTF-8"))
            else:
                fixed.append(decoded[i])
        return fixed

    def select_all(self):
        result = []
        for i in range(0, self.count_records()):
            result.append(self.select(i))

    def delete(self, record_num: int):
        assert record_num < self.count_records(), \
            "Record num is bigger than number of records in the table: {}, {}" \
                .format(record_num, self.count_records())
        record_offset = record_num * self._calculate_record_size()
        data_block = self._get_data_block_with_record(record_num)
        data_block = data_block[0:record_offset % BLOCK_SIZE] + b'd' + data_block[record_offset % BLOCK_SIZE + 1:]
        self._set_data_with_record(record_offset // BLOCK_SIZE, data_block)

    def update(self, index: int, values: Dict[Identifier, Literal]):
        self.insert(values, index)

    def _validate_insert_values(self, values: Dict[Identifier, Literal]):
        """
        ensure all columns of this table are present
        """
        assert values.keys() == {column.name for column in self.get_columns()}

    def _calculate_record_size(self) -> int:
        # s = 1
        # for column in self.get_columns():
        #     if isinstance(column.ty, IntegerTy):
        #         s += 4
        #     elif isinstance(column.ty, FloatTy):
        #         s += 4
        #     elif isinstance(column.ty, VarCharTy):
        #         s += column.ty.width
        #     else:
        #         raise NotImplementedError
        return struct.calcsize(self._make_struct_format_string())

    def _make_struct_format_string(self):
        res = 'c'
        for column in self.get_columns():
            if isinstance(column.ty, IntegerTy):
                res += 'i'
            elif isinstance(column.ty, FloatTy):
                res += 'f'
            elif isinstance(column.ty, VarCharTy):
                res += str(column.ty.width) + 's'
        return res

    def _decode_record(self, data_block, page_offset):
        result = struct.unpack(self._make_struct_format_string(),
                               data_block[page_offset: page_offset + self._calculate_record_size()])
        if result[0] == b'd':
            raise AttributeError("Record is dead")
        elif result[0] == b'a':
            return result[1:]
        else:
            raise RuntimeError("Incorrect record({}): {}".format(page_offset, result))

    def get_column_by_name(self, name: Identifier) -> ColumnDef:
        for column in self.get_columns():
            if column.name == name:
                return column

    def _encode_record(self, values: Dict[Identifier, Literal]):
        """
        assume that value types correspond to column types.
        """
        t = [b'a']  # alive FIXME
        for k, v in values.items():
            if isinstance(v, VarChar):
                t.append(v.value.encode("UTF-8"))
            else:
                t.append(v.value)
        return struct.pack(self._make_struct_format_string(), *t)

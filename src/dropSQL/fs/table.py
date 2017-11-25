"""
Table descriptor structure:
    strz table name
    [
        strz column_name
        u2 column_type
        0 - int
        1..65534 - string length
        65536 - float
    ]
    13 32-bit pointers pointers
"""
import math

from dropSQL.fs.db_file import DBFile
from dropSQL.fs.block import Block
import sys
import struct


class Table:
    def __init__(self, connection: DBFile, index: int):
        self.connection = connection
        self.index = index

    def _load_block(self) -> Block:
        return self.connection.read_block(1 + self.index)

    def _write_block(self, block: Block):
        self.connection.write_block(1 + self.index, block)

    def _decode_descriptor(self) -> dict:
        try:
            block = self._load_block()
        except AssertionError:
            block = Block(b'\0' * 4096)

        table_descriptor = {
            "table_name": (block.data.split(b'\0')[0]).decode("UTF-8"),
            "pointers": [int.from_bytes(block.data[4040 + i * 4:4040 + (i + 1) * 4], byteorder='big')
                         for i in range(0, 13)],
            "records": int.from_bytes(block.data[4092:], byteorder='big')
        }

        columns = []
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
                    purr = "int"
                else:
                    if mjau == 65535:
                        purr = "float"
                    else:
                        purr = "string"
                if purr == "string":
                    columns.append({
                        "name": nyaa,
                        "type": purr,
                        "length": mjau
                    })
                else:
                    columns.append({
                        "name": nyaa,
                        "type": purr
                    })
                i = meow + 3

        table_descriptor["columns"] = columns
        return table_descriptor

    def _encode_descriptor(self, descriptor: dict):
        sys.stderr.write('Encoding: ' + str(descriptor) + '\n')
        data = descriptor["table_name"].encode("UTF-8") + b'\0'
        for col in descriptor["columns"]:
            data += col["name"].encode("UTF-8") + b'\0'
            if col["type"] == "int":
                data += b'\0\0'
            else:
                if col["type"] == "float":
                    data += b'\xff\xff'
                else:
                    data += col["length"].to_bytes(2, byteorder='big')
        while len(data) < 4040:
            data += b'\0'
        for p in descriptor["pointers"]:
            data += p.to_bytes(4, byteorder='big')
        data += descriptor["records"].to_bytes(4, byteorder='big')

        self._write_block(Block(data))

    def get_table_name(self) -> str:
        return self._decode_descriptor()["table_name"]

    def set_table_name(self, new_name: str):
        descriptor = self._decode_descriptor()
        descriptor["table_name"] = new_name
        self._encode_descriptor(descriptor)

    def get_columns(self) -> list:
        return self._decode_descriptor()["columns"]

    def count_records(self):
        return self._decode_descriptor()["records"]

    def add_int_column(self, name):
        descriptor = self._decode_descriptor()
        descriptor["columns"].append({"name": name, "type": "int"})
        self._encode_descriptor(descriptor)

    def add_float_column(self, name):
        descriptor = self._decode_descriptor()
        descriptor["columns"].append({"name": name, "type": "float"})
        self._encode_descriptor(descriptor)

    def add_string_column(self, name, size):
        descriptor = self._decode_descriptor()
        descriptor["columns"].append({"name": name, "type": "string", "length": size})
        self._encode_descriptor(descriptor)

    def _add_block(self):
        self._add_zero_level_block() \
        or self._add_first_level_block() \
        or self._add_second_level_block() \
        or self._add_third_level_block()

    def _add_zero_level_block(self) -> bool:
        descriptor = self._decode_descriptor()
        for i in range(0, 10):
            if descriptor["pointers"][i] == 0:
                descriptor["pointers"][i] = self.connection.allocate_block()
                self._encode_descriptor(descriptor)
                return True
        return False

    def _add_first_level_block(self):
        raise NotImplementedError
        # descriptor = self._decode_descriptor()
        # block_pointer = descriptor["pointers"][11]  # first indirect pointer
        # block = self.connection.read_block(block_pointer)  # pointer block

    def _add_pointer_to_block(self, pointer_to_block: int):
        block = self.connection.read_block(pointer_to_block)
        for i in range(0, 128):
            if int.from_bytes(block[4 * i:4 * (i + 1)], byteorder='big') == 0:
                block = block[:4 * i] \
                        + (self.connection.allocate_block()).to_bytes(4, byteorder='big') \
                        + block[4 * (i + 1):]
                self.connection.write_block(pointer_to_block, block)
                return True
        return False

    def _add_second_level_block(self):
        # TODO
        raise NotImplementedError

    def _add_third_level_block(self):
        # TODO
        raise NotImplementedError

    def _get_data_pointer(self, block_number: int):
        # block numeration from 0
        if block_number < 10:
            # zero level block
            block_pointer = self._decode_descriptor()["pointers"][block_number]
        else:
            if block_number < 10 + 128:
                block_pointer = self._get_block_pointer_1(block_number)
            else:
                if block_number < 10 + 128 + 16384:
                    block_pointer = self._get_block_pointer_2(block_number)
                else:
                    block_pointer = self._get_block_pointer_3(block_number)

        if block_pointer == 0:
            self._add_block()
            return self._get_data_pointer(block_number)
        return block_pointer

    def _get_block_pointer_1(self, block_number):
        # TODO
        raise NotImplementedError

    def _get_block_pointer_2(self, block_number):
        # TODO
        raise NotImplementedError

    def _get_block_pointer_3(self, block_number):
        # TODO
        raise NotImplementedError

    def _increment_record_counter(self):
        descriptor = self._decode_descriptor()
        descriptor["records"] = descriptor["records"] + 1
        self._encode_descriptor(descriptor)

    def _get_data_with_record(self, record_num: int) -> Block:
        page_num = record_num // 4096
        page_offset = record_num % 4096
        data_block = self.connection.read_block(self._get_data_pointer(page_num)).data
        if self._calculate_record_size() + page_offset >= 4096:
            data_block += self.connection.read_block(self._get_data_pointer(page_num + 1)).data
        return data_block

    def _set_data_with_record(self, base_page_num: int, data: bytes):
        self.connection.write_block(self._get_data_pointer(base_page_num), Block(data[0: 4096]))
        if len(data) > 4096:
            self.connection.write_block(self._get_data_pointer(base_page_num + 1), Block(data[4096:]))

    def insert(self, values: dict):
        self._validate_insert_values(values)
        record_num = self.count_records()
        data_block = self._get_data_with_record(record_num)
        page_offset = record_num % 4096
        page_num = record_num // 4096
        record = self._encode_record(values)
        data_block = data_block[0: page_offset] + record + data_block[page_offset + self._calculate_record_size():]
        self._set_data_with_record(page_num, data_block)
        self._increment_record_counter()

    def select(self, record_num: int):
        assert record_num < self.count_records(), \
            "Record num is bigger than number of records in the table: {}, {}" \
                .format(record_num, self.count_records())
        data_block = self._get_data_with_record(record_num)
        decoded = self._decode_record(data_block, record_num % 4096)
        fixed = dict()
        for i in range(0, len(self.get_columns())):
            if type(decoded[i]) == bytes:
                fixed[self.get_columns()[i]["name"]] = decoded[i].split(b'\0')[0].decode("UTF-8")
            else:
                fixed[self.get_columns()[i]["name"]] = decoded[i]
        return fixed

    def _validate_insert_values(self, values):
        # all fields are present:
        values.keys() == {a["name"] for a in self.get_columns()}

    def _calculate_record_size(self) -> int:
        s = 0
        for column in self.get_columns():
            if column["type"] == "int":
                s += 4
            elif column["type"] == "float":
                s += 4
            elif column["type"] == "string":
                s += column["length"]

        return s

    def _make_struct_format_string(self):
        res = ''
        for c in self.get_columns():
            if c["type"] == 'int':
                res += 'i'
            elif c["type"] == 'float':
                res += 'f'
            else:
                res += str(c["length"]) + 's'
        return res

    def _decode_record(self, data_block, page_offset):
        return struct.unpack(self._make_struct_format_string(),
                             data_block[page_offset: page_offset + self._calculate_record_size()])

    def _get_type_by_column_name(self, name: str):
        for d in self.get_columns():
            if d["name"] == name:
                return d["type"]

    def _encode_record(self, values: dict):
        t = ()
        for k, v in values.items():
            if self._get_type_by_column_name(k) == "string":
                t += (v.encode("UTF-8"),)
            else:
                t += (v,)

        return struct.pack(self._make_struct_format_string(), *t)

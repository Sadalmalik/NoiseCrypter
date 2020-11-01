#!/usr/bin/python
# coding=utf-8

import io


def get_bit(value, idx):
    result = (value >> idx) & 1
    # print(f"get_bit test {idx}")
    # print(f"    {value:08b}")
    # print(f"    {(1<<idx):08b}")
    # print(f"    {result}")
    return result


def set_bit(value, idx, bit):
    stored = value
    if bit == 0:
        value = value & ~(1 << idx)
    else:
        value = value | (1 << idx)
    # print(f"set_bit test {idx}:{bit}")
    # print(f"    {value:08b}")
    # print(f"    {stored:08b}")
    # print(f"    {value ^ stored:08b}")
    return value


class BitStream:
    def __init__(self, data=None, encoding="utf8"):
        if isinstance(data, str):
            data = bytes(data, encoding='utf8')
        self._stream = io.BytesIO(data)
        self._byte = None
        self._byte_offset = 0
        self._empty = False

    @property
    def base_stream(self):
        return self._stream

    @property
    def is_empty(self):
        return self._empty

    def read(self):
        if self._empty:
            return None
        if self._byte is None:
            self._byte = self._stream.read(1)
            if self._byte is None or len(self._byte) == 0:
                self._empty = True
                self._byte = None
                return None
            self._byte = int(self._byte[0])
            self._byte_offset = 0
        bit = get_bit(self._byte, 7 - self._byte_offset)
        self._byte_offset += 1
        if self._byte_offset >= 8:
            self._byte = None
        return bit

    def read_bits(self, k):
        bits = 0
        count = 0
        while count < k:
            bit = self.read()
            if bit is None:
                break
            bits = set_bit(bits, k - count - 1, bit)
            count += 1
        return bits

    def write(self, value):
        if self._byte is None:
            self._byte = 0
            self._byte_offset = 0
        self._byte = set_bit(self._byte, 7 - self._byte_offset, value)
        self._byte_offset += 1
        if self._byte_offset >= 8:
            self._stream.write(self._byte.to_bytes(1, byteorder='big'))
            self._byte = None

    def write_bits(self, k, bits):
        count = 0
        while count < k:
            bit = get_bit(bits, k - count - 1)
            self.write(bit)
            count += 1

    def flush(self):
        if self._byte is not None:
            self._stream.write(self._byte.to_bytes(1, byteorder='big'))
            self._byte = None
        self._stream.flush()

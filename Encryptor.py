#!/usr/bin/python
# coding=utf-8

import random

from BitStream import BitStream, get_bit

default_min_head = 2
default_max_head = 7


def to_bits(value, k):
    count = 0
    result = []
    while count < k:
        bit = get_bit(value, k - count - 1)
        result.append(bit)
        count += 1
    return result


class Encryptor:
    def __init__(self, key, **kwargs):
        self._base_cryptor = random.Random()
        self._base_cryptor.seed(key)
        self._output_stream = BitStream()
        global default_min_head
        global default_max_head
        self._min_header = kwargs.get("min_header", default_min_head)
        self._max_header = kwargs.get("max_header", default_max_head)
        self._debug = kwargs.get("debug", False)

    def write(self, message):
        crypter = self._base_cryptor

        noise = random.Random()
        src = BitStream(message)
        dst = self._output_stream

        while True:
            head_size = crypter.randint(
                self._min_header,
                self._max_header)
            body_size = noise.getrandbits(head_size)
            body_size = max(1, body_size)

            content = []
            count = 0
            while count < body_size:
                bit = src.read()
                if bit is None:
                    break
                count += 1
                bit ^= crypter.getrandbits(1)
                content.append(bit)
            body_size = count

            if body_size == 0:
                break

            if self._debug:
                head_bits = ''.join(str(i) for i in to_bits(body_size, head_size))
                body_bits = ''.join(str(i) for i in content)
                print(f"Encryptor: head {head_size: 4d}, body {body_size: 4d} : [{head_bits}] [{body_bits}]")

            dst.write_bits(head_size, body_size)
            for bit in content:
                dst.write(bit)


    def close(self):
        crypter = self._base_cryptor
        dst = self._output_stream

        head_size = crypter.randint(
            self._min_header,
            self._max_header)
        dst.write_bits(head_size, 0)
        dst.flush()

    def get_data(self):
        stream = self._output_stream
        stream.base_stream.seek(0)
        result = stream.base_stream.read()
        return result


class Decryptor:
    def __init__(self, key, **kwargs):
        self._base_cryptor = random.Random()
        self._base_cryptor.seed(key)
        self._output_stream = BitStream()
        global default_min_head
        global default_max_head
        self._min_header = kwargs.get("min_header", default_min_head)
        self._max_header = kwargs.get("max_header", default_max_head)
        self._debug = kwargs.get("debug", False)

    def read(self, data):
        crypter = self._base_cryptor

        src = BitStream(data)
        dst = self._output_stream

        while True:
            head_size = crypter.randint(
                self._min_header,
                self._max_header)
            body_size = src.read_bits(head_size)

            if body_size == 0:
                break

            count = 0
            content = []
            while count < body_size:
                bit = src.read()
                if bit is None:
                    raise Exception("Unexpected end of stream!")
                count += 1
                if self._debug:
                    content.append(bit)
                bit ^= crypter.getrandbits(1)
                dst.write(bit)

            # dst.flush()

            if self._debug:
                head_bits = ''.join(str(i) for i in to_bits(body_size, head_size))
                body_bits = ''.join(str(i) for i in content)
                print(f"Decryptor: head {head_size: 4d}, body {body_size: 4d} : [{head_bits}] [{body_bits}]")

        dst.flush()

    def get_data(self):
        stream = self._output_stream
        stream.base_stream.seek(0)
        result = stream.base_stream.read()
        stream.base_stream.seek(0)
        return result


def Encrypt(key, message, **kwargs):
    enc = Encryptor(key, **kwargs)
    enc.write(message)
    enc.close()
    data = enc.get_data()
    return data


def Decrypt(key, datagramm, **kwargs):
    dec = Decryptor(key, **kwargs)
    dec.read(datagramm)
    data = dec.get_data()
    return data

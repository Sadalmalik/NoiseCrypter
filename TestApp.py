#!/usr/bin/python
# coding=utf-8

from io import BytesIO
from BitStream import *
from Encryptor import Encrypt, Decrypt, Encryptor, Decryptor


def test_encryption():
    data = "Hello, сосиска!!"

    key = 100500
    print(f"Key: {key}")

    for i in range(10):
        datagramm = Encrypt(key, data)
        result = Decrypt(key, datagramm)

        print(f"  test: {data} -> {datagramm.hex()} -> {str(result, encoding='utf8')}")
        # print(f"{datagramm.hex()}\n")

def test_encryption_2():
    key = 100500

    enc = Encryptor(key)
    enc.write("Сообщение первое")
    enc.write("Сообщение второе")
    enc.write("Сообщение третье")
    enc.close()
    datagramm = enc.get_data()

    dec = Decryptor(key)
    dec.read(datagramm)
    message_1 = dec.get_data()
    dec.read(datagramm)
    message_2 = dec.get_data()
    dec.read(datagramm)
    message_3 = dec.get_data()
    print(datagramm.hex())
    print(f"  {str(message_1, encoding='utf8')}")
    print(f"  {str(message_2, encoding='utf8')}")
    print(f"  {str(message_3, encoding='utf8')}")


if __name__ == "__main__":
    # test_hex()
    # test_streams()
    test_encryption()
    # test_encryption_2()
    # BytesTests()

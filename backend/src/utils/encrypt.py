#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

from typing import Any

from cryptography.hazmat.backends.openssl import backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from itsdangerous import URLSafeSerializer

from src.common.log import log


class AESCipher:
    def __init__(self, key: bytes | str):
        """
        :param key: The key, 16/24/32 bytes or a hexadecimal string
        """
        self.key = key if isinstance(key, bytes) else bytes.fromhex(key) # type: ignore

    def encrypt(self, plaintext: bytes | str) -> bytes:
        """
        AES Encryption

        :param plaintext: The plaintext to be encrypted
        :return: Encrypted ciphertext
        """
        if not isinstance(plaintext, bytes):
            plaintext = str(plaintext).encode('utf-8')
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=backend)
        encryptor = cipher.encryptor()
        padder = padding.PKCS7(cipher.algorithm.block_size).padder() # type: ignore
        padded_plaintext = padder.update(plaintext) + padder.finalize()
        ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()
        return iv + ciphertext

    def decrypt(self, ciphertext: bytes | str) -> str:
        """
        AES Decryption

        :param ciphertext: The ciphertext to be decrypted, bytes or hexadecimal string
        :return: Decrypted plaintext
        """
        ciphertext = ciphertext if isinstance(ciphertext, bytes) else bytes.fromhex(ciphertext) # type: ignore
        iv = ciphertext[:16]
        ciphertext = ciphertext[16:]
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=backend)
        decryptor = cipher.decryptor()
        unpadder = padding.PKCS7(cipher.algorithm.block_size).unpadder() # type: ignore
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
        return plaintext.decode('utf-8')


class Md5Cipher:
    @staticmethod
    def encrypt(plaintext: bytes | str) -> str:
        """
        MD5 Encryption

        :param plaintext: The plaintext to be encrypted
        :return: Encrypted ciphertext
        """
        import hashlib

        md5 = hashlib.md5()
        if not isinstance(plaintext, bytes):
            plaintext = str(plaintext).encode('utf-8')
        md5.update(plaintext)
        return md5.hexdigest()


class ItsDCipher:
    def __init__(self, key: bytes | str):
        """
        :param key: The key, 16/24/32 bytes or a hexadecimal string
        """
        self.key = key if isinstance(key, bytes) else bytes.fromhex(key) # type: ignore

    def encrypt(self, plaintext: Any) -> str:
        """
        ItsDangerous Encryption (may fail, if plaintext cannot be serialized, it will encrypt to MD5)

        :param plaintext: The plaintext to be encrypted
        :return: Encrypted ciphertext
        """
        serializer = URLSafeSerializer(self.key)
        try:
            ciphertext = serializer.dumps(plaintext)
        except Exception as e:
            log.error(f'ItsDangerous encrypt failed: {e}')
            ciphertext = Md5Cipher.encrypt(plaintext)
        return ciphertext # type: ignore

    def decrypt(self, ciphertext: str) -> Any:
        """
        ItsDangerous Decryption (may fail, if ciphertext cannot be deserialized, decryption will fail and return the original ciphertext)

        :param ciphertext: The ciphertext to be decrypted
        :return: Decrypted plaintext
        """
        serializer = URLSafeSerializer(self.key)
        try:
            plaintext = serializer.loads(ciphertext)
        except Exception as e:
            log.error(f'ItsDangerous decrypt failed: {e}')
            plaintext = ciphertext
        return plaintext

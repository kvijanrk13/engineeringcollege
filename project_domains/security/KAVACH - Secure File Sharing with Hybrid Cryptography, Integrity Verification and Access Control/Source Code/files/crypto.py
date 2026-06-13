import base64
import os
from dataclasses import dataclass

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


@dataclass(frozen=True)
class EncryptedFilePayload:
    ciphertext: bytes
    aes_key: str
    nonce: str


def encrypt_file_bytes(file_bytes):
    aes_key = AESGCM.generate_key(bit_length=256)
    nonce = os.urandom(12)
    aesgcm = AESGCM(aes_key)
    ciphertext = aesgcm.encrypt(nonce, file_bytes, None)

    return EncryptedFilePayload(
        ciphertext=ciphertext,
        aes_key=base64.b64encode(aes_key).decode("ascii"),
        nonce=base64.b64encode(nonce).decode("ascii"),
    )


def decrypt_file_bytes(ciphertext, aes_key, nonce):
    decoded_key = base64.b64decode(aes_key.encode("ascii"))
    decoded_nonce = base64.b64decode(nonce.encode("ascii"))
    return AESGCM(decoded_key).decrypt(decoded_nonce, ciphertext, None)

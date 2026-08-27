"""
Authenticated encryption for sensitive fields (e.g. bot tokens).

Payload layout (all fields concatenated, stored as raw bytes):
  [version: 1 byte] [salt: 16 bytes] [nonce: 12 bytes] [ciphertext+GCM tag: n+16 bytes]

- version  : SECRET_KEY_VERSION from env, allows rotation without re-encrypting all rows at once
- salt     : random per-record; fed into HKDF so each record has a unique derived key
- nonce    : random per-encryption; prevents ciphertext reuse even if derived key is reused
             (redundant given per-record salt, but kept for defense-in-depth at negligible cost)
- ciphertext + GCM tag: AES-256-GCM output; tag authenticates integrity
"""

import base64
import secrets

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

SALT_LEN = 16
NONCE_LEN = 12
HEADER_LEN = 1 + SALT_LEN + NONCE_LEN  # 29 bytes


def encrypt(plaintext: str, master_key: str, version: int) -> bytes:
    """
    Encrypt plaintext string using AES-256-GCM with a per-record derived key.

    master_key is a base64url-encoded string without padding (SECRET_KEY env var).
    version is the key version (SECRET_KEY_VERSION env var).
    Returns raw bytes ready for LargeBinary storage.
    """
    salt = secrets.token_bytes(SALT_LEN)
    nonce = secrets.token_bytes(NONCE_LEN)
    ciphertext = AESGCM(_derive_key(_b64url_decode(master_key), salt)).encrypt(
        nonce, plaintext.encode(), None
    )
    return bytes([version]) + salt + nonce + ciphertext


def decrypt(data: bytes, master_key: str) -> str:
    """
    Decrypt bytes produced by encrypt().

    master_key is a base64url-encoded string without padding (SECRET_KEY env var).
    Raises ValueError if the payload is malformed.
    Raises cryptography.exceptions.InvalidTag if the ciphertext was tampered with.
    """
    if len(data) <= HEADER_LEN:
        raise ValueError(
            f"Encrypted payload is too short: got {len(data)} bytes, expected >{HEADER_LEN}"
        )

    salt = data[1 : 1 + SALT_LEN]
    nonce = data[1 + SALT_LEN : HEADER_LEN]
    ciphertext = data[HEADER_LEN:]
    return (
        AESGCM(_derive_key(_b64url_decode(master_key), salt))
        .decrypt(nonce, ciphertext, None)
        .decode()
    )


def encrypt_b64(plaintext: str, master_key: str, version: int) -> str:
    """
    Encrypt and return base64url text without padding, ready for a Text column.
    """
    return (
        base64.urlsafe_b64encode(encrypt(plaintext, master_key, version))
        .decode()
        .rstrip("=")
    )


def decrypt_b64(data: str, master_key: str) -> str:
    """
    Decrypt a value produced by encrypt_b64(). Accepts padded and unpadded input.
    """
    return decrypt(_b64url_decode(data), master_key)


def _b64url_decode(value: str) -> bytes:
    missing = len(value) % 4
    if missing:
        value += "=" * (4 - missing)
    return base64.urlsafe_b64decode(value)


def _derive_key(master_key: bytes, salt: bytes) -> bytes:
    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        info=None,
    ).derive(master_key)

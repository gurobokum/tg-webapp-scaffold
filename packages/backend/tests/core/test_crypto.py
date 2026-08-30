import base64
import secrets

import pytest
from cryptography.exceptions import InvalidTag

from app.core.crypto import HEADER_LEN, decrypt, decrypt_b64, encrypt, encrypt_b64

KEY = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b"=").decode()
VERSION = 1


def test_roundtrip() -> None:
    token = "1234567890:ABCDefghIJKLmnopQRSTuvwxYZ"
    assert decrypt(encrypt(token, KEY, VERSION), KEY) == token


def test_each_encryption_produces_different_ciphertext() -> None:
    token = "same-token"
    assert encrypt(token, KEY, VERSION) != encrypt(token, KEY, VERSION)


def test_version_byte_is_stored() -> None:
    data = encrypt("token", KEY, VERSION)
    assert data[0] == VERSION


def test_payload_length() -> None:
    token = "short"
    data = encrypt(token, KEY, VERSION)
    assert len(data) == HEADER_LEN + len(token.encode()) + 16


def test_wrong_key_raises() -> None:
    data = encrypt("token", KEY, VERSION)
    other_key = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b"=").decode()
    with pytest.raises(InvalidTag):
        decrypt(data, other_key)


def test_tampered_ciphertext_raises() -> None:
    data = bytearray(encrypt("token", KEY, VERSION))
    data[-1] ^= 0xFF
    with pytest.raises(InvalidTag):
        decrypt(bytes(data), KEY)


def test_short_payload_raises() -> None:
    with pytest.raises(ValueError, match="too short"):
        decrypt(b"tooshort", KEY)


def test_b64_roundtrip() -> None:
    token = "1234567890:ABCDefghIJKLmnopQRSTuvwxYZ"
    assert decrypt_b64(encrypt_b64(token, KEY, VERSION), KEY) == token


def test_b64_has_no_padding() -> None:
    data = encrypt_b64("token", KEY, VERSION)
    assert "=" not in data


def test_b64_accepts_padded_and_unpadded() -> None:
    data = encrypt_b64("token", KEY, VERSION)
    padded = data + "=" * (-len(data) % 4)
    assert decrypt_b64(data, KEY) == "token"
    assert decrypt_b64(padded, KEY) == "token"


def test_master_key_without_padding() -> None:
    raw = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
    key_no_padding = raw.rstrip("=")
    token = "test-token"
    assert decrypt(encrypt(token, key_no_padding, VERSION), key_no_padding) == token

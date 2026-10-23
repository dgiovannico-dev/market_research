"""Fernet helpers — master key from CREDENTIALS_MASTER_KEY env only."""

from __future__ import annotations

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import get_settings


class CredentialsCryptoError(RuntimeError):
    """Master key missing/invalid or decrypt failed."""


def _fernet() -> Fernet:
    key = (get_settings().credentials_master_key or "").strip()
    if not key:
        raise CredentialsCryptoError("CREDENTIALS_MASTER_KEY is not set")
    try:
        return Fernet(key.encode("utf-8") if isinstance(key, str) else key)
    except (ValueError, TypeError) as exc:
        raise CredentialsCryptoError("CREDENTIALS_MASTER_KEY is invalid") from exc


def encrypt_bytes(plaintext: bytes) -> bytes:
    return _fernet().encrypt(plaintext)


def decrypt_bytes(ciphertext: bytes) -> bytes:
    try:
        return _fernet().decrypt(ciphertext)
    except InvalidToken as exc:
        raise CredentialsCryptoError("ciphertext decrypt failed") from exc

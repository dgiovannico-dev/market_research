"""Persist / load encrypted connector credential rows (never log values)."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.secrets.crypto import CredentialsCryptoError, decrypt_bytes, encrypt_bytes
from app.secrets.schema import all_fields
from app.storage.models_core import SourceCredential

log = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def row_exists(db: Session, connector_key: str) -> bool:
    return db.get(SourceCredential, connector_key) is not None


def load_secrets(db: Session, connector_key: str) -> Optional[dict[str, str]]:
    """Decrypt DB row or None if missing. Empty dict if decrypt fails (fail closed)."""
    row = db.get(SourceCredential, connector_key)
    if row is None:
        return None
    try:
        raw = decrypt_bytes(bytes(row.ciphertext))
        data = json.loads(raw.decode("utf-8"))
    except (CredentialsCryptoError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        log.warning("credential decrypt failed for connector_key=%s (%s)", connector_key, type(exc).__name__)
        return {}
    if not isinstance(data, dict):
        return {}
    allowed = set(all_fields(connector_key))
    out: dict[str, str] = {}
    for k, v in data.items():
        if k in allowed and v is not None:
            s = str(v).strip()
            if s:
                out[k] = s
    return out


def save_secrets(
    db: Session,
    connector_key: str,
    fields: dict[str, Any],
    *,
    updated_by: Optional[str] = None,
) -> None:
    allowed = all_fields(connector_key)
    if not allowed:
        raise ValueError(f"unknown connector_key: {connector_key}")
    cleaned: dict[str, str] = {}
    for name in allowed:
        if name not in fields:
            continue
        val = fields[name]
        if val is None:
            continue
        s = str(val).strip()
        if s:
            cleaned[name] = s
    # Merge with existing so partial updates keep other fields
    existing = load_secrets(db, connector_key)
    if existing:
        merged = {**existing, **cleaned}
    else:
        merged = cleaned
    # If caller sent empty string for a field, drop it
    for name in allowed:
        if name in fields and (fields[name] is None or str(fields[name]).strip() == ""):
            merged.pop(name, None)
    payload = json.dumps(merged, separators=(",", ":"), sort_keys=True).encode("utf-8")
    token = encrypt_bytes(payload)
    row = db.get(SourceCredential, connector_key)
    label = (updated_by or "").strip()[:128] or None
    if row is None:
        row = SourceCredential(
            connector_key=connector_key,
            ciphertext=token,
            updated_at=_now(),
            updated_by=label,
        )
        db.add(row)
    else:
        row.ciphertext = token
        row.updated_at = _now()
        row.updated_by = label
    db.commit()
    log.info("credentials saved connector_key=%s fields=%s", connector_key, sorted(merged.keys()))


def delete_secrets(db: Session, connector_key: str) -> bool:
    row = db.get(SourceCredential, connector_key)
    if row is None:
        return False
    db.delete(row)
    db.commit()
    log.info("credentials deleted connector_key=%s", connector_key)
    return True


def field_presence(db: Session, connector_key: str) -> dict[str, bool]:
    """Which allowlisted fields are set (no values)."""
    secrets = load_secrets(db, connector_key)
    if secrets is None:
        return {name: False for name in all_fields(connector_key)}
    return {name: bool(secrets.get(name)) for name in all_fields(connector_key)}

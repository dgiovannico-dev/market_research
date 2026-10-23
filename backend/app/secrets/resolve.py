"""Resolve connector secrets: DB ciphertext wins when row exists, else env."""

from __future__ import annotations

import logging
from typing import Literal, Optional

from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.secrets.schema import CONNECTOR_SECRET_FIELDS, all_fields, required_fields
from app.secrets.store import load_secrets, row_exists

log = logging.getLogger(__name__)

CredentialsSource = Literal["db", "env", "none"]


def _env_bundle(connector_key: str, settings: Settings) -> dict[str, str]:
    """Map Settings env fields → schema field names (secrets only)."""
    s = settings
    mapping: dict[str, dict[str, str]] = {
        "adzuna": {
            "app_id": s.adzuna_app_id,
            "app_key": s.adzuna_app_key,
        },
        "usajobs": {
            "api_key": s.usajobs_api_key,
            "user_agent": s.usajobs_user_agent,
        },
        "france_travail": {
            "client_id": s.france_travail_client_id,
            "client_secret": s.france_travail_client_secret,
        },
        "bundesagentur": {"api_key": s.bundesagentur_api_key},
        "jooble": {"api_key": s.jooble_api_key},
        "findwork": {"api_key": s.findwork_api_key},
        "findajob_dwp": {
            "api_id": s.findajob_dwp_api_id,
            "api_key": s.findajob_dwp_api_key,
        },
        "freelancer": {"oauth_token": s.freelancer_oauth_token},
        "upwork": {
            "oauth_token": s.upwork_oauth_token,
            "tenant_id": s.upwork_tenant_id,
        },
        "careerjet": {
            "api_key": s.careerjet_api_key,
            "user_ip": s.careerjet_user_ip,
        },
        "infojobs": {
            "client_id": s.infojobs_client_id,
            "client_secret": s.infojobs_client_secret,
        },
    }
    raw = mapping.get(connector_key) or {}
    return {k: v.strip() for k, v in raw.items() if v and str(v).strip()}


def _db_bundle(session: Session, connector_key: str) -> Optional[dict[str, str]]:
    """Return secrets if a DB row exists (authoritative), else None to signal env fallback."""
    if not row_exists(session, connector_key):
        return None
    return dict(load_secrets(session, connector_key) or {})


def _open_session_bundle(connector_key: str) -> Optional[dict[str, str]]:
    """Try DB via composition root; on connection errors return None (caller uses env)."""
    try:
        from app.bootstrap import get_container

        with get_container().session_scope() as session:
            return _db_bundle(session, connector_key)
    except Exception as exc:  # noqa: BLE001 — env fallback when DB down in unit tests
        log.debug("credential DB lookup skipped: %s", type(exc).__name__)
        return None


def credential_bundle(
    connector_key: str,
    *,
    db: Optional[Session] = None,
    settings: Optional[Settings] = None,
) -> dict[str, str]:
    """Secret fields for a connector. DB row authoritative when present."""
    if connector_key not in CONNECTOR_SECRET_FIELDS:
        return {}
    cfg = settings or get_settings()
    if db is not None:
        db_vals = _db_bundle(db, connector_key)
        if db_vals is not None:
            return db_vals
        return _env_bundle(connector_key, cfg)
    db_vals = _open_session_bundle(connector_key)
    if db_vals is not None:
        return db_vals
    return _env_bundle(connector_key, cfg)


def _source_from_bundle(
    connector_key: str,
    *,
    from_db: bool,
    bundle: dict[str, str],
) -> CredentialsSource:
    req = required_fields(connector_key)
    if from_db:
        if req and all(bundle.get(f) for f in req):
            return "db"
        if any(bundle.get(f) for f in all_fields(connector_key)):
            return "db"
        return "none"
    if req and all(bundle.get(f) for f in req):
        return "env"
    if any(bundle.values()):
        return "env"
    return "none"


def credentials_source(
    connector_key: str,
    *,
    db: Optional[Session] = None,
    settings: Optional[Settings] = None,
) -> CredentialsSource:
    if connector_key not in CONNECTOR_SECRET_FIELDS:
        return "none"
    cfg = settings or get_settings()

    def _from_session(session: Session) -> CredentialsSource:
        if row_exists(session, connector_key):
            secrets = load_secrets(session, connector_key) or {}
            return _source_from_bundle(connector_key, from_db=True, bundle=secrets)
        env = _env_bundle(connector_key, cfg)
        return _source_from_bundle(connector_key, from_db=False, bundle=env)

    if db is not None:
        return _from_session(db)
    try:
        from app.bootstrap import get_container

        with get_container().session_scope() as session:
            return _from_session(session)
    except Exception:  # noqa: BLE001
        env = _env_bundle(connector_key, cfg)
        return _source_from_bundle(connector_key, from_db=False, bundle=env)


def has_required_credentials(
    connector_key: str,
    *,
    db: Optional[Session] = None,
    settings: Optional[Settings] = None,
) -> bool:
    req = required_fields(connector_key)
    if not req:
        return True
    bundle = credential_bundle(connector_key, db=db, settings=settings)
    return all(bool(bundle.get(f)) for f in req)

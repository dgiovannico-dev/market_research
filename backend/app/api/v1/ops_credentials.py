"""Ops endpoints for encrypted connector credentials (no plaintext responses)."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import require_admin, verify_api_key
from app.collectors.registry import CREDENTIALED_SCAFFOLDS
from app.secrets.crypto import CredentialsCryptoError
from app.secrets.resolve import credentials_source, has_required_credentials
from app.secrets.schema import all_fields, required_fields
from app.secrets.store import delete_secrets, field_presence, save_secrets
from app.storage.db import get_db
from app.storage.models_core import SourceCredential

router = APIRouter(prefix="/api/v1", dependencies=[Depends(verify_api_key)])


class CredentialsPutBody(BaseModel):
    fields: dict[str, str] = Field(default_factory=dict)
    ops_label: Optional[str] = None


def _require_scaffold(key: str) -> None:
    if key not in CREDENTIALED_SCAFFOLDS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unknown credentialed connector",
        )


@router.get(
    "/ops/connectors/{connector_key}/credential-fields",
    dependencies=[Depends(require_admin)],
)
def credential_fields(
    connector_key: str,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Field names + set/unset (masked). Requires admin JWT or OPS break-glass."""
    _require_scaffold(connector_key)
    presence = field_presence(db, connector_key)
    row = db.get(SourceCredential, connector_key)
    return {
        "connector_key": connector_key,
        "credentials_source": credentials_source(connector_key, db=db),
        "credentials_present": has_required_credentials(connector_key, db=db),
        "required": list(required_fields(connector_key)),
        "fields": {
            name: {"set": bool(presence.get(name)), "required": name in required_fields(connector_key)}
            for name in all_fields(connector_key)
        },
        "updated_at": row.updated_at.isoformat() if row and row.updated_at else None,
        "updated_by": row.updated_by if row else None,
    }


@router.put(
    "/ops/connectors/{connector_key}/credentials",
    dependencies=[Depends(require_admin)],
)
def put_credentials(
    connector_key: str,
    body: CredentialsPutBody,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    _require_scaffold(connector_key)
    allowed = set(all_fields(connector_key))
    unknown = sorted(set(body.fields) - allowed)
    if unknown:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown fields: {', '.join(unknown)}",
        )
    try:
        save_secrets(
            db,
            connector_key,
            body.fields,
            updated_by=(body.ops_label or "ops-ui")[:128],
        )
    except CredentialsCryptoError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return {
        "connector_key": connector_key,
        "credentials_present": has_required_credentials(connector_key, db=db),
        "credentials_source": credentials_source(connector_key, db=db),
        "fields_set": sorted(
            name for name, on in field_presence(db, connector_key).items() if on
        ),
    }


@router.delete(
    "/ops/connectors/{connector_key}/credentials",
    dependencies=[Depends(require_admin)],
)
def delete_credentials(
    connector_key: str,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    _require_scaffold(connector_key)
    deleted = delete_secrets(db, connector_key)
    return {
        "connector_key": connector_key,
        "deleted": deleted,
        "credentials_present": has_required_credentials(connector_key, db=db),
        "credentials_source": credentials_source(connector_key, db=db),
    }

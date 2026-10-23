"""DTO mapping for research intents."""

from __future__ import annotations

from typing import Any

from app.storage.models import SearchQuery


def serialize_intent(row: SearchQuery) -> dict[str, Any]:
    return {
        "id": row.id,
        "name": row.name,
        "label": row.name,
        "query_text": row.query_text,
        "kind": row.kind,
        "countries": row.countries or [],
        "role_families": row.role_families or [],
        "contract_types": row.contract_types or [],
        "filters_extra": row.filters_extra,
        "enabled": row.enabled,
        "schedule_hint": row.schedule_hint,
        "origin": row.origin,
        "version": row.version,
        "deleted_at": row.deleted_at.isoformat() if row.deleted_at else None,
        "created_at": row.created_at.isoformat() if row.created_at else None,
        "updated_at": row.updated_at.isoformat() if row.updated_at else None,
    }

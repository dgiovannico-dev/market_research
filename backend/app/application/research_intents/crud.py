"""CRUD commands for research intents (SearchQuery rows)."""

from __future__ import annotations

from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.research_intent.policies import (
    VALID_KINDS,
    apply_soft_delete,
    bump_version,
    resolve_display_name,
)
from app.storage.models import SearchQuery


class IntentNotFoundError(LookupError):
    """Active (non-deleted) research intent missing."""


def get_active_intent(db: Session, intent_id: int) -> SearchQuery:
    row = db.get(SearchQuery, intent_id)
    if not row or row.deleted_at is not None:
        raise IntentNotFoundError("Research intent not found")
    return row


def list_research_intents(
    db: Session,
    *,
    kind: Optional[str] = None,
    include_deleted: bool = False,
) -> list[SearchQuery]:
    if kind is not None and kind not in VALID_KINDS:
        raise ValueError("kind must be discovery or focus")
    stmt = select(SearchQuery).order_by(SearchQuery.id)
    if not include_deleted:
        stmt = stmt.where(SearchQuery.deleted_at.is_(None))
    if kind is not None:
        stmt = stmt.where(SearchQuery.kind == kind)
    return list(db.scalars(stmt).all())


def create_research_intent(
    db: Session,
    *,
    name: Optional[str] = None,
    label: Optional[str] = None,
    query_text: str,
    kind: str,
    countries: Optional[list[str]] = None,
    role_families: Optional[list[str]] = None,
    contract_types: Optional[list[str]] = None,
    filters_extra: Optional[dict[str, Any]] = None,
    enabled: bool = True,
    schedule_hint: str = "daily",
    origin: str = "user",
) -> SearchQuery:
    text = (query_text or "").strip()
    if not text:
        raise ValueError("query_text is required for search-mode intents")
    if kind not in VALID_KINDS:
        raise ValueError("kind must be discovery or focus")
    display = resolve_display_name(name=name, label=label)
    row = SearchQuery(
        name=display,
        query_text=text,
        kind=kind,
        countries=list(countries or []),
        role_families=list(role_families or []),
        contract_types=list(contract_types or []),
        filters_extra=filters_extra,
        enabled=enabled,
        schedule_hint=schedule_hint,
        origin=origin,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def patch_research_intent(
    db: Session,
    intent_id: int,
    updates: dict[str, Any],
) -> SearchQuery:
    row = get_active_intent(db, intent_id)
    data = dict(updates)
    if "query_text" in data:
        text = str(data["query_text"]).strip()
        if not text:
            raise ValueError("query_text cannot be blank")
        data["query_text"] = text
    if "name" in data:
        data["name"] = str(data["name"]).strip()
    if "kind" in data and data["kind"] not in VALID_KINDS:
        raise ValueError("kind must be discovery or focus")
    for key, value in data.items():
        setattr(row, key, value)
    bump_version(row)
    db.commit()
    db.refresh(row)
    return row


def soft_delete_research_intent(db: Session, intent_id: int) -> SearchQuery:
    row = get_active_intent(db, intent_id)
    apply_soft_delete(row)
    db.commit()
    return row

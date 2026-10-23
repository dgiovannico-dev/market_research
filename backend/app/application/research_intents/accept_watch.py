"""Accept an LLM suggest_watches candidate as a persisted intent."""

from __future__ import annotations

from typing import Any, Optional

from sqlalchemy.orm import Session

from app.application.research_intents.crud import create_research_intent
from app.storage.models import SearchQuery


def accept_watch_suggestion(
    db: Session,
    *,
    name: Optional[str] = None,
    label: Optional[str] = None,
    query_text: str,
    kind: str = "focus",
    countries: Optional[list[str]] = None,
    role_families: Optional[list[str]] = None,
    contract_types: Optional[list[str]] = None,
    filters_extra: Optional[dict[str, Any]] = None,
    schedule_hint: str = "daily",
    enabled: bool = True,
) -> SearchQuery:
    text = (query_text or "").strip()
    if not text:
        raise ValueError("query_text is required")
    return create_research_intent(
        db,
        name=name,
        label=label,
        query_text=text,
        kind=kind,
        countries=countries,
        role_families=role_families,
        contract_types=contract_types,
        filters_extra=filters_extra,
        enabled=enabled,
        schedule_hint=schedule_hint,
        origin="llm_accepted",
    )

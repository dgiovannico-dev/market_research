"""Research Intent HTTP adapter — Demand Compass discovery / focus + DB Explore."""

from __future__ import annotations

from typing import Any, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import verify_api_key
from app.application.research_intents import (
    accept_watch_suggestion,
    create_research_intent,
    get_active_intent,
    list_research_intents,
    patch_research_intent,
    rematch_intents,
    serialize_intent,
    soft_delete_research_intent,
    sync_research_intent,
)
from app.application.research_intents.crud import IntentNotFoundError
from app.research.country_suggest import suggested_countries_from_intents
from app.research.jobs_facets import research_job_facets
from app.research.jobs_search import search_research_jobs
from app.storage.db import get_db

router = APIRouter(prefix="/api/v1", dependencies=[Depends(verify_api_key)])

IntentKind = Literal["discovery", "focus"]
ScheduleHint = Literal["daily", "manual_only"]
Origin = Literal["seed_discovery", "seed_focus", "user", "llm_accepted"]


class IntentCreate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=128)
    label: Optional[str] = Field(default=None, min_length=1, max_length=128)
    query_text: str = Field(min_length=1)
    kind: IntentKind
    countries: list[str] = Field(default_factory=list)
    role_families: list[str] = Field(default_factory=list)
    contract_types: list[str] = Field(default_factory=list)
    filters_extra: Optional[dict[str, Any]] = None
    enabled: bool = True
    schedule_hint: ScheduleHint = "daily"
    origin: Origin = "user"


class IntentPatch(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=128)
    query_text: Optional[str] = Field(default=None, min_length=1)
    kind: Optional[IntentKind] = None
    countries: Optional[list[str]] = None
    role_families: Optional[list[str]] = None
    contract_types: Optional[list[str]] = None
    filters_extra: Optional[dict[str, Any]] = None
    enabled: Optional[bool] = None
    schedule_hint: Optional[ScheduleHint] = None
    origin: Optional[Origin] = None


class AcceptWatchBody(BaseModel):
    """LLM suggest_watches candidate → persist as enabled intent."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=128)
    label: Optional[str] = Field(default=None, min_length=1, max_length=128)
    query_text: str = Field(min_length=1)
    kind: IntentKind = "focus"
    countries: list[str] = Field(default_factory=list)
    role_families: list[str] = Field(default_factory=list)
    contract_types: list[str] = Field(default_factory=list)
    filters_extra: Optional[dict[str, Any]] = None
    schedule_hint: ScheduleHint = "daily"
    enabled: bool = True


def _http_value_error(exc: ValueError) -> HTTPException:
    return HTTPException(400, str(exc))


def _http_not_found(exc: IntentNotFoundError) -> HTTPException:
    return HTTPException(404, str(exc) or "Research intent not found")


@router.get("/research/intents")
def list_intents(
    kind: Optional[IntentKind] = Query(default=None),
    include_deleted: bool = Query(default=False),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    try:
        rows = list_research_intents(db, kind=kind, include_deleted=include_deleted)
    except ValueError as exc:
        raise _http_value_error(exc) from exc
    return {
        "items": [serialize_intent(r) for r in rows],
        "total": len(rows),
        # Hint for CountryFilter UI — never auto-applied by the API.
        "suggested_countries": suggested_countries_from_intents(rows),
    }


@router.post("/research/intents", status_code=201)
def create_intent(body: IntentCreate, db: Session = Depends(get_db)) -> dict[str, Any]:
    try:
        row = create_research_intent(
            db,
            name=body.name,
            label=body.label,
            query_text=body.query_text,
            kind=body.kind,
            countries=body.countries,
            role_families=body.role_families,
            contract_types=body.contract_types,
            filters_extra=body.filters_extra,
            enabled=body.enabled,
            schedule_hint=body.schedule_hint,
            origin=body.origin,
        )
    except ValueError as exc:
        raise _http_value_error(exc) from exc
    return serialize_intent(row)


@router.patch("/research/intents/{intent_id}")
def patch_intent(
    intent_id: int, body: IntentPatch, db: Session = Depends(get_db)
) -> dict[str, Any]:
    try:
        row = patch_research_intent(
            db, intent_id, body.model_dump(exclude_unset=True)
        )
    except IntentNotFoundError as exc:
        raise _http_not_found(exc) from exc
    except ValueError as exc:
        raise _http_value_error(exc) from exc
    return serialize_intent(row)


@router.delete("/research/intents/{intent_id}")
def delete_intent(intent_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
    try:
        row = soft_delete_research_intent(db, intent_id)
    except IntentNotFoundError as exc:
        raise _http_not_found(exc) from exc
    return {
        "status": "deleted",
        "id": intent_id,
        "deleted_at": row.deleted_at.isoformat() if row.deleted_at else None,
    }


@router.post("/research/intents/{intent_id}/sync")
async def sync_intent(intent_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
    try:
        row = get_active_intent(db, intent_id)
    except IntentNotFoundError as exc:
        raise _http_not_found(exc) from exc
    return await sync_research_intent(db, row)


@router.post("/research/matches/backfill")
def backfill_matches(
    kind: Literal["focus", "discovery", "all"] = Query(
        default="all",
        description="Use all after dump ingest so focus-only matches do not empty market",
    ),
    enabled_only: bool = Query(default=True),
    dry_run: bool = Query(default=False),
    limit_jobs: Optional[int] = Query(default=None, ge=1, le=50_000),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Rematch existing canonical jobs to intents (no crawl). Prefer after dump ingest."""
    return rematch_intents(
        db,
        kind=kind,
        enabled_only=enabled_only,
        dry_run=dry_run,
        limit_jobs=limit_jobs,
    )


@router.post("/research/watches/accept", status_code=201)
def accept_watch(body: AcceptWatchBody, db: Session = Depends(get_db)) -> dict[str, Any]:
    try:
        row = accept_watch_suggestion(
            db,
            name=body.name,
            label=body.label,
            query_text=body.query_text,
            kind=body.kind,
            countries=body.countries,
            role_families=body.role_families,
            contract_types=body.contract_types,
            filters_extra=body.filters_extra,
            schedule_hint=body.schedule_hint,
            enabled=body.enabled,
        )
    except ValueError as exc:
        raise _http_value_error(exc) from exc
    return serialize_intent(row)


@router.get("/research/jobs/facets")
def research_jobs_facets(
    query_id: Optional[int] = Query(default=None),
    lens: Optional[Literal["market", "focus", "compare"]] = Query(default=None),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Distinct countries, sources, contracts, remotes for Jobs filters."""
    return research_job_facets(db, query_id=query_id, lens=lens)


@router.get("/research/jobs")
def research_jobs(
    q: Optional[str] = Query(default=None),
    query_id: Optional[int] = Query(default=None),
    lens: Optional[Literal["market", "focus", "compare"]] = Query(default=None),
    country_code: Optional[str] = Query(
        default=None,
        description="ISO country code or CSV (e.g. IT,CH)",
    ),
    source_id: Optional[str] = Query(
        default=None,
        description="Source id or CSV of ids",
    ),
    contract_type: Optional[str] = Query(
        default=None,
        description="Contract type or CSV",
    ),
    remote_type: Optional[str] = Query(
        default=None,
        description="Remote type or CSV",
    ),
    sort: Optional[str] = Query(
        default="published_at",
        description="published_at|title|company|country_code|contract_type|source",
    ),
    order: Optional[Literal["asc", "desc"]] = Query(default="desc"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    include_closed: bool = Query(
        default=False,
        description="Include closed / stale / removed-from-source jobs",
    ),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """DB-only Explore search (Job + JobIntentMatch). Does not crawl sources.

    Returns ``total``, ``items``, and echoes ``skip`` / ``limit``.
    """
    return search_research_jobs(
        db,
        q=q,
        query_id=query_id,
        lens=lens,
        country_code=country_code,
        source_id=source_id,
        contract_type=contract_type,
        remote_type=remote_type,
        sort=sort,
        order=order,
        skip=skip,
        limit=limit,
        include_closed=include_closed,
    )

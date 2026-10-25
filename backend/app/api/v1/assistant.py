"""HTTP bridge for propose/materialize + Demand Compass evidence briefs.

Locale: optional ``en``|``it`` is accepted and echoed in ``meta.locale``.
MVP evidence narratives remain English (``meta.narrative_locale`` = ``en``);
UI chrome stays next-intl. KPI numbers are never re-localized or invented.
"""

from __future__ import annotations

from typing import Any, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import verify_api_key
from app.application.assistant import (
    materialize_report,
    propose_dashboard,
    propose_report,
    validate_spec,
)
from app.application.assistant.specs import ReportSpec
from app.application.briefs import BRIEF_TYPES, render_brief
from app.storage.db import get_db

router = APIRouter(prefix="/api/v1", dependencies=[Depends(verify_api_key)])

BriefType = Literal[
    "rising_cooling",
    "where_demand",
    "adjacent",
    "focus_vs_market",
    "suggest_watches",
]
LensType = Literal["market", "focus", "compare"]
LocaleType = Literal["en", "it"]

# Brief/report narrative language for MVP (handlers are English-only today).
_NARRATIVE_LOCALE_MVP: LocaleType = "en"


class ProposeBody(BaseModel):
    prompt: str = Field(default="", max_length=4000)
    kind: Literal["dashboard", "report", "brief"] = "dashboard"
    materialize: bool = False
    brief_type: Optional[BriefType] = None
    lens: Optional[LensType] = None
    query_ids: Optional[list[int]] = None
    period_days: int = Field(default=90, ge=1, le=365)
    # CSV ISO codes — same contract as market/summary ?country_code=
    country_code: Optional[str] = Field(default=None, max_length=64)
    locale: LocaleType = "en"
    # Client localStorage skills (ADR-009) for adjacent / suggest_watches
    owned_skills: Optional[list[str]] = None


class BriefBody(BaseModel):
    brief_type: BriefType
    lens: Optional[LensType] = None
    query_ids: Optional[list[int]] = None
    period_days: int = Field(default=90, ge=1, le=365)
    prompt: str = Field(default="", max_length=4000)
    # CSV ISO codes — same contract as market/summary ?country_code=
    country_code: Optional[str] = Field(default=None, max_length=64)
    locale: LocaleType = "en"
    # Client localStorage skills (ADR-009) for adjacent / suggest_watches
    owned_skills: Optional[list[str]] = None


def _locale_meta(locale: LocaleType) -> dict[str, Any]:
    return {
        "locale": locale,
        "narrative_locale": _NARRATIVE_LOCALE_MVP,
    }


def _run_brief(db: Session, body: BriefBody | ProposeBody) -> dict[str, Any]:
    brief_type = body.brief_type
    if not brief_type:
        raise HTTPException(400, "brief_type is required for evidence briefs")
    if brief_type not in BRIEF_TYPES:
        raise HTTPException(400, f"unknown brief_type; valid={sorted(BRIEF_TYPES)}")
    result = render_brief(
        db,
        brief_type=brief_type,
        lens=body.lens,
        query_ids=body.query_ids,
        period_days=body.period_days,
        country_code=body.country_code,
        owned_skills=body.owned_skills,
    )
    return {"kind": "brief", "brief": result, "meta": _locale_meta(body.locale)}


@router.post("/assistant/propose")
def assistant_propose(body: ProposeBody, db: Session = Depends(get_db)) -> dict[str, Any]:
    if body.kind == "brief" or body.brief_type is not None:
        return _run_brief(db, body)

    if not body.prompt or not body.prompt.strip():
        raise HTTPException(400, "prompt is required for dashboard/report propose")

    meta = _locale_meta(body.locale)
    if body.kind == "dashboard":
        spec = propose_dashboard(body.prompt)
        validation = validate_spec(spec)
        return {
            "kind": "dashboard",
            "spec": spec.model_dump(),
            "validation": validation.to_dict(),
            "materialized": None,
            "meta": meta,
        }
    spec_r = propose_report(body.prompt)
    validation = validate_spec(spec_r)
    materialized: Optional[dict[str, Any]] = None
    if body.materialize:
        materialized = materialize_report(db, spec_r)
    return {
        "kind": "report",
        "spec": spec_r.model_dump(),
        "validation": validation.to_dict(),
        "materialized": materialized,
        "meta": meta,
    }


@router.post("/assistant/brief")
def assistant_brief(body: BriefBody, db: Session = Depends(get_db)) -> dict[str, Any]:
    """Structured evidence-coach brief (SPEC-research-intents J5)."""
    return _run_brief(db, body)


@router.post("/assistant/chat")
def assistant_chat(body: BriefBody, db: Session = Depends(get_db)) -> dict[str, Any]:
    """Alias of /assistant/brief for chat-style clients requesting brief_type."""
    return _run_brief(db, body)


@router.post("/assistant/validate")
def assistant_validate(spec: dict[str, Any]) -> dict[str, Any]:
    return validate_spec(spec).to_dict()


@router.post("/assistant/materialize-report")
def assistant_materialize(spec: dict[str, Any], db: Session = Depends(get_db)) -> dict[str, Any]:
    return materialize_report(db, ReportSpec.model_validate(spec))

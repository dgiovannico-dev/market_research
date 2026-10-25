"""Admin LLM runtime + prompt registry (ADR-010)."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.adapters.driven.llm.provider import provider_from_settings
from app.api.deps import get_optional_principal, require_admin, verify_api_key
from app.auth.oidc import AuthPrincipal
from app.application.llm.prompts import (
    activate_version,
    archive_version,
    create_version,
    delete_version,
    ensure_seed_prompts,
    list_templates,
)
from app.application.llm.runtime_config import (
    RUNTIME_ROW_ID,
    resolve_llm_settings,
    settings_public_dict,
    upsert_runtime_config,
)
from app.storage.db import get_db
from app.storage.models_llm import LlmRuntimeConfig

router = APIRouter(prefix="/api/v1", dependencies=[Depends(verify_api_key)])


def _actor(principal: AuthPrincipal | None) -> Optional[str]:
    if principal is None:
        return "ops"
    return principal.sub or principal.email or "admin"


class LlmSettingsPut(BaseModel):
    provider: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = Field(default=None, ge=0, le=2)
    timeout_s: Optional[int] = Field(default=None, ge=5, le=600)
    max_tokens: Optional[int] = Field(default=None, ge=1, le=128000)
    api_key: Optional[str] = None
    clear_api_key: bool = False
    enable_classify: Optional[bool] = None
    enable_weekly_report: Optional[bool] = None
    enable_study_advisor: Optional[bool] = None
    enable_brief_narrative: Optional[bool] = None


class PromptVersionCreate(BaseModel):
    system_text: str = ""
    user_text: str = ""
    notes: Optional[str] = None
    activate: bool = False


@router.get("/ops/llm/settings", dependencies=[Depends(require_admin)])
def get_llm_settings(db: Session = Depends(get_db)) -> dict[str, Any]:
    resolved = resolve_llm_settings(db)
    row = db.get(LlmRuntimeConfig, RUNTIME_ROW_ID)
    return settings_public_dict(resolved, row)


@router.put("/ops/llm/settings", dependencies=[Depends(require_admin)])
async def put_llm_settings(
    body: LlmSettingsPut,
    db: Session = Depends(get_db),
    principal: AuthPrincipal | None = Depends(get_optional_principal),
) -> dict[str, Any]:
    try:
        row = upsert_runtime_config(
            db,
            payload=body.model_dump(exclude_unset=True),
            actor=_actor(principal),
        )
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001 — crypto / DB
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=f"failed to save LLM settings: {exc}",
        ) from exc
    resolved = resolve_llm_settings(db)
    return {"status": "saved", **settings_public_dict(resolved, row)}


@router.post("/ops/llm/test", dependencies=[Depends(require_admin)])
async def test_llm(db: Session = Depends(get_db)) -> dict[str, Any]:
    cfg = resolve_llm_settings(db)
    provider = provider_from_settings(cfg)
    health = await provider.health()
    return {"health": health, "provider": cfg.provider, "source": cfg.source}


@router.get("/ops/llm/prompts", dependencies=[Depends(require_admin)])
def get_prompts(db: Session = Depends(get_db)) -> dict[str, Any]:
    return {"items": list_templates(db)}


@router.post("/ops/llm/prompts/seed", dependencies=[Depends(require_admin)])
def seed_prompts(db: Session = Depends(get_db)) -> dict[str, Any]:
    return ensure_seed_prompts(db)


@router.post("/ops/llm/prompts/{slug}/versions", dependencies=[Depends(require_admin)])
def post_prompt_version(
    slug: str,
    body: PromptVersionCreate,
    db: Session = Depends(get_db),
    principal: AuthPrincipal | None = Depends(get_optional_principal),
) -> dict[str, Any]:
    try:
        return create_version(
            db,
            slug=slug,
            system_text=body.system_text,
            user_text=body.user_text,
            notes=body.notes,
            actor=_actor(principal),
            activate=body.activate,
        )
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post(
    "/ops/llm/prompts/versions/{version_id}/activate",
    dependencies=[Depends(require_admin)],
)
def post_activate_version(
    version_id: int,
    db: Session = Depends(get_db),
    principal: AuthPrincipal | None = Depends(get_optional_principal),
) -> dict[str, Any]:
    try:
        return activate_version(db, version_id=version_id, actor=_actor(principal))
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post(
    "/ops/llm/prompts/versions/{version_id}/archive",
    dependencies=[Depends(require_admin)],
)
def post_archive_version(
    version_id: int,
    db: Session = Depends(get_db),
    principal: AuthPrincipal | None = Depends(get_optional_principal),
) -> dict[str, Any]:
    try:
        return archive_version(db, version_id=version_id, actor=_actor(principal))
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.delete(
    "/ops/llm/prompts/versions/{version_id}",
    dependencies=[Depends(require_admin)],
)
def delete_prompt_version(
    version_id: int,
    db: Session = Depends(get_db),
    principal: AuthPrincipal | None = Depends(get_optional_principal),
) -> dict[str, Any]:
    try:
        return delete_version(db, version_id=version_id, actor=_actor(principal))
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


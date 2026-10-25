"""Ops-driven LLM classification overlay on top of domain rules."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.adapters.driven.llm.provider import get_llm_provider
from app.application.llm.prompts import resolve_prompt
from app.application.llm.runtime_config import resolve_llm_settings
from app.application.ports.driven.llm_gateway import LlmGateway
from app.domain.classification import classify_job
from app.storage.models import Job


class LlmJobExtraction(BaseModel):
    role_family: str | None = None
    seniority: str | None = None
    contract_type: str | None = None
    remote_type: str | None = None
    technologies_required: list[str] = Field(default_factory=list)
    technologies_preferred: list[str] = Field(default_factory=list)
    confidence: float | None = None
    ambiguities: list[str] = Field(default_factory=list)


async def run_llm_classification(
    db: Session,
    *,
    limit: int = 20,
    llm: LlmGateway | None = None,
) -> dict[str, Any]:
    cfg = resolve_llm_settings(db)
    provider = llm or get_llm_provider(db)
    health = await provider.health()
    if cfg.provider == "none" or not cfg.enable_classify or not health.get("healthy"):
        return {
            "status": "skipped",
            "reason": "LLM offline, disabled, or provider=none; rules classification remains active",
            "health": health,
        }

    try:
        prompt = resolve_prompt(
            db,
            slug="classify_job",
            variables={"schema_keys": str(list(LlmJobExtraction.model_json_schema().get("properties", {}).keys()))},
        )
    except ValueError:
        prompt = None

    jobs = db.scalars(
        select(Job).where(Job.is_canonical.is_(True)).order_by(Job.id.desc()).limit(limit)
    ).all()
    results = []
    for job in jobs:
        rules = classify_job(
            title=job.title_original,
            description=job.description_original,
            location=job.location_original,
        )
        text = f"{job.title_original}\n{job.description_original or ''}"
        validated = None
        error = None
        try:
            if prompt:
                raw_text = await provider.chat(
                    [
                        {"role": "system", "content": prompt["system"]},
                        {
                            "role": "user",
                            "content": prompt["user"].replace("{{text}}", text[:12000])
                            if "{{text}}" in prompt["user"]
                            else f"{prompt['user']}\n\nTEXT:\n{text[:12000]}",
                        },
                    ],
                    response_json=True,
                )
                import json

                raw = json.loads(raw_text or "{}")
            else:
                raw = await provider.classify_text(
                    text,
                    schema_hint=LlmJobExtraction.model_json_schema(),
                )
            try:
                validated = LlmJobExtraction.model_validate(raw)
            except ValidationError:
                raw = await provider.classify_text(
                    text + "\nReturn ONLY valid JSON for the schema.",
                    schema_hint=LlmJobExtraction.model_json_schema(),
                )
                validated = LlmJobExtraction.model_validate(raw)
            if validated.contract_type:
                job.contract_type = validated.contract_type
                job.contract_evidence_kind = "inferred"
                job.contract_type_confidence = validated.confidence
            if validated.remote_type:
                job.remote_type = validated.remote_type
            if validated.seniority:
                job.seniority = validated.seniority
            if validated.role_family:
                job.role_family = validated.role_family
            job.classification_version = f"hybrid-{provider.name}-1.0.0"
        except Exception as exc:  # noqa: BLE001
            error = str(exc)
            job.classification_version = rules.classification_version
        results.append(
            {
                "job_id": job.id,
                "rules_contract": rules.contract_type,
                "llm": validated.model_dump() if validated else None,
                "error": error,
            }
        )
    db.commit()
    return {
        "status": "completed",
        "processed": len(results),
        "results": results,
        "health": health,
        "prompt_version": prompt.get("version") if prompt else None,
    }

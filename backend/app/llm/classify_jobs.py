from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.classification.rules import classify_job
from app.core.config import get_settings
from app.llm.provider import get_llm_provider
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


async def run_llm_classification(db: Session, *, limit: int = 20) -> dict[str, Any]:
    settings = get_settings()
    provider = get_llm_provider()
    health = await provider.health()
    if settings.llm_provider == "none" or not health.get("healthy"):
        return {
            "status": "skipped",
            "reason": "LLM offline or provider=none; rules classification remains active",
            "health": health,
        }

    jobs = db.scalars(
        select(Job).where(Job.is_canonical.is_(True)).order_by(Job.id.desc()).limit(limit)
    ).all()
    results = []
    for job in jobs:
        # Always keep rules baseline
        rules = classify_job(
            title=job.title_original,
            description=job.description_original,
            location=job.location_original,
        )
        text = f"{job.title_original}\n{job.description_original or ''}"
        raw = None
        validated = None
        error = None
        try:
            raw = await provider.classify_text(
                text,
                schema_hint=LlmJobExtraction.model_json_schema(),
            )
            try:
                validated = LlmJobExtraction.model_validate(raw)
            except ValidationError:
                # one repair attempt
                raw = await provider.classify_text(
                    text + "\nReturn ONLY valid JSON for the schema.",
                    schema_hint=LlmJobExtraction.model_json_schema(),
                )
                validated = LlmJobExtraction.model_validate(raw)
            # Apply only non-null LLM fields as inferred overlay (do not invent rates)
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
    return {"status": "completed", "processed": len(results), "results": results, "health": health}

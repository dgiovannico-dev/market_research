"""Materialize ReportSpec with observed analytics grounding."""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.application.assistant.observed import get_observed_counts
from app.application.assistant.specs import ReportSpec
from app.application.assistant.validate import validate_spec


def materialize_report(db: Session, spec: ReportSpec | dict) -> dict[str, Any]:
    if isinstance(spec, dict):
        spec = ReportSpec.model_validate(spec)
    validation = validate_spec(spec)
    if not validation.ok:
        return {"ok": False, "errors": validation.errors, "spec": spec.model_dump()}

    counts = get_observed_counts(db, spec.period_days)
    jobs_n = int(counts.get("unique_jobs_in_period") or 0)
    rates_n = int(counts.get("jobs_with_rate_in_period") or 0)

    sections_out: list[dict[str, Any]] = []
    for sec in spec.sections:
        data: dict[str, Any] = {"kind": sec.kind, "title": sec.title or sec.kind}
        if sec.kind == "summary":
            data["data"] = {
                "unique_jobs_in_period": jobs_n,
                "sources_enabled": counts.get("sources_enabled"),
            }
            data["insufficient_data"] = jobs_n == 0
        elif sec.kind == "rates":
            data["data"] = {"jobs_with_rate_in_period": rates_n}
            data["insufficient_data"] = rates_n == 0
            if rates_n == 0:
                data["note"] = (
                    "No declared rates in period; median/percentiles are undeclared "
                    "(not zero). Do not invent EUR/CHF figures."
                )
        elif sec.kind == "sources":
            data["data"] = {
                "sources_total": counts.get("sources_total"),
                "sources_enabled": counts.get("sources_enabled"),
            }
            data["insufficient_data"] = False
        elif sec.kind == "skills":
            data["data"] = {"filter_hint": "use GET /api/v1/market/trends"}
            data["insufficient_data"] = jobs_n == 0
        elif sec.kind == "gaps":
            data["data"] = {"endpoint": "GET /api/v1/profile/skill-gaps"}
            data["insufficient_data"] = False
        else:
            data["data"] = {}
            data["insufficient_data"] = jobs_n == 0
        sections_out.append(data)

    narrative = _narrative(jobs_n, rates_n, counts)
    return {
        "ok": True,
        "spec": spec.model_dump(),
        "counts": counts,
        "sections": sections_out,
        "narrative": narrative,
        "warnings": validation.warnings,
        "evidence_kind": "observed",
    }


def _narrative(jobs_n: int, rates_n: int, counts: dict[str, Any]) -> str:
    if jobs_n == 0:
        return (
            "Insufficient observed jobs in the selected period. "
            "No market size or rates can be inferred. Run collectors or widen the period."
        )
    parts = [
        f"Observed {jobs_n} unique jobs in the last {counts.get('period_days')} days "
        f"from this database ({counts.get('sources_enabled')} enabled sources)."
    ]
    if rates_n == 0:
        parts.append(
            "Declared compensation is missing for this sample; rates are undeclared, not zero."
        )
    else:
        parts.append(
            f"{rates_n} jobs have at least one declared rate record "
            "(use rates endpoints for percentiles; NULL excluded)."
        )
    parts.append("These figures are not estimates of total market demand.")
    return " ".join(parts)

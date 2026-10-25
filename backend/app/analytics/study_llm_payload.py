"""Compact / coerce Study Advisor payloads for small-context LLMs."""

from __future__ import annotations

import json
from typing import Any


def coerce_llm_plan_payload(
    data: dict[str, Any],
    *,
    evidence: dict[str, Any],
) -> dict[str, Any]:
    """Normalize common small-model JSON mistakes before StudyPlan validation."""
    out = dict(data)

    def _as_str_list(value: Any) -> list[str]:
        if value is None:
            return []
        if isinstance(value, list):
            items: list[str] = []
            for item in value:
                if isinstance(item, str) and item.strip():
                    items.append(item.strip())
                elif isinstance(item, dict):
                    name = item.get("technology") or item.get("skill") or item.get("name")
                    if name and str(name).strip():
                        items.append(str(name).strip())
            return items
        if isinstance(value, str):
            return [
                p.strip()
                for p in value.replace(" and ", ",").replace("/", ",").split(",")
                if p.strip()
            ]
        return []

    out["stack_target"] = _as_str_list(out.get("stack_target"))

    milestones_raw = out.get("milestones")
    cleaned_ms: list[dict[str, Any]] = []
    if isinstance(milestones_raw, list):
        for i, m in enumerate(milestones_raw):
            if not isinstance(m, dict):
                continue
            week = m.get("week")
            try:
                week_i = int(week) if week is not None else (i + 1) * 2
            except (TypeError, ValueError):
                week_i = (i + 1) * 2
            title = m.get("title") or m.get("name") or m.get("skill") or f"Milestone {week_i}"
            skills = _as_str_list(m.get("skills") or m.get("skill"))
            if not skills and isinstance(m.get("technology"), str):
                skills = [m["technology"].strip()]
            refs = m.get("evidence_refs")
            if not isinstance(refs, list):
                refs = [f"candidate:{s}" for s in skills]
            entry: dict[str, Any] = {
                "week": max(1, week_i),
                "title": str(title),
                "skills": skills,
                "evidence_refs": [str(r) for r in refs if r],
            }
            if m.get("hours") is not None:
                try:
                    entry["hours"] = float(m["hours"])
                except (TypeError, ValueError):
                    pass
            cleaned_ms.append(entry)
    out["milestones"] = cleaned_ms

    if not isinstance(out.get("limits"), list):
        lim = out.get("limits")
        out["limits"] = [str(lim)] if lim else []
    if not isinstance(out.get("weekly_template"), list):
        out["weekly_template"] = []

    out.setdefault("modality", evidence.get("modality"))
    out.setdefault("hours_per_week", evidence.get("hours_per_week"))
    out.setdefault("horizon_weeks", evidence.get("horizon_weeks"))
    if not out.get("title"):
        out["title"] = "Study plan"
    return out


def compact_evidence_for_llm(
    evidence: dict[str, Any],
    *,
    max_candidates: int = 8,
    max_certs: int = 6,
    max_chars: int = 4500,
) -> str:
    """Shrink evidence JSON so small-context local models (≤4k tokens) can ingest it.

    Full evidence packs include drilldowns, rate histograms, and repeated limits that
    routinely blow past 4096 input tokens when dumped raw.
    """
    slim_cands: list[dict[str, Any]] = []
    for c in (evidence.get("candidates") or [])[:max_candidates]:
        if not isinstance(c, dict):
            continue
        rate = c.get("rate_check") if isinstance(c.get("rate_check"), dict) else {}
        rate_median = None
        if isinstance(rate.get("rate"), dict):
            rate_median = rate["rate"].get("median")
        slim_cands.append(
            {
                "technology": c.get("technology"),
                "anchor_skill": c.get("anchor_skill"),
                "support": c.get("support"),
                "lift": c.get("lift"),
                "gap_priority": c.get("gap_priority"),
                "score": c.get("score"),
                "irreplaceability_score": c.get("irreplaceability_score"),
                "growth_pct": c.get("growth_pct"),
                "rate_median": rate_median,
                "rate_n": rate.get("sample_size"),
            }
        )
    slim_certs: list[dict[str, Any]] = []
    for cert in (evidence.get("related_certifications") or [])[:max_certs]:
        if not isinstance(cert, dict):
            continue
        slim_certs.append(
            {
                "slug": cert.get("slug"),
                "display_name": cert.get("display_name"),
                "mentions": cert.get("mentions"),
            }
        )
    pack = {
        "modality": evidence.get("modality"),
        "hours_per_week": evidence.get("hours_per_week"),
        "horizon_weeks": evidence.get("horizon_weeks"),
        "skills": evidence.get("skills") or [],
        "certifications": evidence.get("certifications") or [],
        "coverage": evidence.get("coverage") or {},
        "candidates": slim_cands,
        "related_certifications": slim_certs,
        "limits": list(evidence.get("limits") or [])[:8],
        "disclaimer": evidence.get("disclaimer"),
    }
    raw = json.dumps(pack, default=str, separators=(",", ":"))
    if len(raw) <= max_chars:
        return raw
    pack["related_certifications"] = slim_certs[:3]
    pack["candidates"] = slim_cands[:5]
    pack["limits"] = pack["limits"][:4]
    raw = json.dumps(pack, default=str, separators=(",", ":"))
    if len(raw) <= max_chars:
        return raw
    return raw[:max_chars]

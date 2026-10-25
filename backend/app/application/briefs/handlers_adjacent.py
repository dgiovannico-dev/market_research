"""Adjacent-skills and watch-suggestion brief handlers."""

from __future__ import annotations

from typing import Any, Optional, Sequence

from sqlalchemy.orm import Session

from app.analytics import kpis
from app.analytics.cooccurrence import skill_cooccurrence
from app.application.briefs.human_narrative import (
    adjacent_narrative,
    normalize_locale,
    suggest_watches_narrative,
)
from app.application.briefs.support import (
    DEFAULT_LENS,
    MIN_SAMPLE,
    THIN_SAMPLE,
    base_payload,
    countries_extra,
    flat_lens,
    geo_label,
    lens_excluded_thin_n,
    lens_sample_size,
    profile_skill_names,
    status_for_n,
    thin_or_refuse,
    with_evidence_limits,
)


def adjacent(
    db: Session,
    *,
    lens: str = DEFAULT_LENS,
    query_ids: Optional[Sequence[int]] = None,
    period_days: int = 90,
    country_code: Optional[str] = None,
    owned_skills: Optional[Sequence[str]] = None,
    locale: str = "en",
) -> dict[str, Any]:
    loc = normalize_locale(locale)
    n = lens_sample_size(
        db,
        lens=lens,
        query_ids=query_ids,
        days=period_days,
        country_code=country_code,
    )
    excluded = lens_excluded_thin_n(
        db,
        lens=lens,
        query_ids=query_ids,
        days=period_days,
        country_code=country_code,
    )
    limits = with_evidence_limits(
        "Adjacent skills from co-occurrence near profile skills not yet owned. "
        "Co-occurrence ≠ causation."
    )
    refused = thin_or_refuse(
        brief_type="adjacent",
        lens=lens,
        sample_size=n,
        limits=limits,
        excluded_thin_n=excluded,
        extra=countries_extra(country_code),
        locale=loc,
    )
    if refused:
        return refused

    if owned_skills is not None:
        owned = {s.strip() for s in owned_skills if s and str(s).strip()}
    else:
        owned = profile_skill_names(db)
    alens = flat_lens(lens)
    co = skill_cooccurrence(
        db,
        days=period_days,
        min_support=MIN_SAMPLE,
        country_code=country_code,
        lens=alens,
        query_ids=query_ids,
    )
    candidates: list[dict[str, Any]] = []
    if owned:
        for row in co.get("items", []):
            a, b = row["tech_a"], row["tech_b"]
            if a in owned and b not in owned:
                candidates.append({**row, "owned": a, "adjacent": b})
            elif b in owned and a not in owned:
                candidates.append({**row, "owned": b, "adjacent": a})
        candidates.sort(key=lambda x: (-x["support"], -(x.get("lift") or 0)))
        candidates = candidates[:15]

    evidence = [
        {
            "metric": "skill_cooccurrence",
            "owned_skills": sorted(owned),
            "jobs_analyzed": co.get("jobs_analyzed"),
            "items": candidates,
            "source": "skill_cooccurrence",
            "countries": co.get("countries"),
        }
    ]
    status = status_for_n(n)
    narrative = adjacent_narrative(
        locale=loc,
        lens=lens,
        n=n,
        owned=bool(owned),
        candidates=candidates,
        min_support=MIN_SAMPLE,
        thin=status == "thin_sample",
        thin_threshold=THIN_SAMPLE,
        geo=geo_label(country_code),
    )
    return base_payload(
        brief_type="adjacent",
        lens=lens,
        sample_size=n,
        evidence=evidence,
        narrative=narrative,
        limits=limits,
        status=status,
        excluded_thin_n=excluded,
        extra=countries_extra(country_code),
    )


def suggest_watches(
    db: Session,
    *,
    lens: str = DEFAULT_LENS,
    query_ids: Optional[Sequence[int]] = None,
    period_days: int = 90,
    country_code: Optional[str] = None,
    owned_skills: Optional[Sequence[str]] = None,
    locale: str = "en",
) -> dict[str, Any]:
    """Propose intents only — never INSERT SearchQuery."""
    loc = normalize_locale(locale)
    n = lens_sample_size(
        db,
        lens=lens,
        query_ids=query_ids,
        days=period_days,
        country_code=country_code,
    )
    excluded = lens_excluded_thin_n(
        db,
        lens=lens,
        query_ids=query_ids,
        days=period_days,
        country_code=country_code,
    )
    limits = with_evidence_limits(
        "Proposed watches are suggestions from co-occurrence. "
        "Nothing is persisted until POST /research/watches/accept."
    )
    refused = thin_or_refuse(
        brief_type="suggest_watches",
        lens=lens,
        sample_size=n,
        limits=limits,
        excluded_thin_n=excluded,
        extra=countries_extra(country_code),
        locale=loc,
    )
    if refused:
        return refused

    if owned_skills is not None:
        owned = {s.strip() for s in owned_skills if s and str(s).strip()}
    else:
        owned = profile_skill_names(db)
    alens = flat_lens(lens)
    co = skill_cooccurrence(
        db,
        days=period_days,
        min_support=MIN_SAMPLE,
        country_code=country_code,
        lens=alens,
        query_ids=query_ids,
    )
    proposed: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in co.get("items", [])[:40]:
        for side, other in ((row["tech_a"], row["tech_b"]), (row["tech_b"], row["tech_a"])):
            if owned and side not in owned:
                continue
            if other in owned or other in seen:
                continue
            seen.add(other)
            proposed.append(
                {
                    "name": f"Watch {other}",
                    "query_text": other,
                    "kind": "focus",
                    "rationale": (
                        f"Co-occurs with {side} (support={row['support']}, "
                        f"lift={row.get('lift')})"
                    ),
                    "support": row["support"],
                    "anchor_skill": side,
                    "origin_hint": "llm_suggest",
                }
            )
            if len(proposed) >= 8:
                break
        if len(proposed) >= 8:
            break

    if not proposed:
        trends = kpis.technology_trends(
            db,
            days=period_days,
            min_support=MIN_SAMPLE,
            country_code=country_code,
            lens=alens,
            query_ids=query_ids,
        )
        for t in trends.get("items", []):
            name = t.get("technology")
            if not name or name in owned or t.get("status") != "ok":
                continue
            proposed.append(
                {
                    "name": f"Watch {name}",
                    "query_text": name,
                    "kind": "discovery",
                    "rationale": (
                        f"Rising/active mentions (growth={t.get('growth_pct')}, "
                        f"n={t.get('sample_size')})"
                    ),
                    "support": t.get("sample_size"),
                    "anchor_skill": None,
                    "origin_hint": "llm_suggest",
                }
            )
            if len(proposed) >= 5:
                break

    status = status_for_n(n)
    narrative = suggest_watches_narrative(
        locale=loc,
        lens=lens,
        n=n,
        proposed_count=len(proposed),
        min_support=MIN_SAMPLE,
        thin=status == "thin_sample",
        thin_threshold=THIN_SAMPLE,
        geo=geo_label(country_code),
    )

    return base_payload(
        brief_type="suggest_watches",
        lens=lens,
        sample_size=n,
        evidence=[
            {
                "metric": "skill_cooccurrence",
                "jobs_analyzed": co.get("jobs_analyzed"),
                "owned_skills": sorted(owned),
                "source": "skill_cooccurrence",
                "countries": co.get("countries"),
            }
        ],
        narrative=narrative,
        limits=limits,
        status=status,
        excluded_thin_n=excluded,
        extra={**countries_extra(country_code), "proposed_intents": proposed},
    )

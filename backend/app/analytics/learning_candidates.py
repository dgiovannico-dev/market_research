"""Learning candidates: gaps + co-occurrence + rise/cool + irreplaceability."""

from __future__ import annotations

from typing import Any, Optional, Sequence

from sqlalchemy.orm import Session

from app.analytics.certifications import top_certifications
from app.analytics.cooccurrence import skill_cooccurrence
from app.analytics.irreplaceability import (
    STACK_COMPASS_SCORE_VERSION,
    score_components_for_candidate,
)
from app.analytics.kpis import technology_trends
from app.analytics.lenses import compare_counts, parse_lens
from app.analytics.positioning import skill_gaps
from app.analytics.rate_for_tech import rate_for_technology
from app.analytics.skill_ownership import resolve_owned_skill_names
from app.core.config import get_settings

_MIN_SUPPORT = 2
_RATE_N_MIN = 5


def _growth_boost(status: Optional[str], growth_pct: Any) -> float:
    """Map rise/cool into [0,1] growth component for scoring weights."""
    if status == "rising":
        try:
            g = float(growth_pct) if growth_pct is not None else 0.0
        except (TypeError, ValueError):
            g = 0.0
        return min(1.0, max(0.15, g / 100.0 if abs(g) > 1 else abs(g)))
    if status == "cooling":
        return 0.05
    if status == "ok":
        return 0.35
    return 0.2


def _learning_candidates_flat(
    db: Session,
    *,
    owned_skills: list[str],
    days: int,
    country_code: Optional[str],
    lens: Optional[str],
    query_ids: Optional[Sequence[int]],
    min_evidence: Optional[str],
    top_n: int,
    owned_certifications: Optional[list[str]],
    include_rates: bool,
) -> dict[str, Any]:
    owned = resolve_owned_skill_names(owned_skills)
    settings = get_settings()
    gaps_payload = skill_gaps(
        db,
        days=days,
        country_code=country_code,
        owned_skills=list(owned),
    )
    if gaps_payload.get("error"):
        return {
            **gaps_payload,
            "candidates": [],
            "related_certifications": [],
            "score_version": STACK_COMPASS_SCORE_VERSION,
        }

    demand_by_tech: dict[str, float] = {}
    for g in gaps_payload.get("gaps") or []:
        name = g.get("technology")
        if not name:
            continue
        demand_by_tech[str(name)] = float(g.get("priority_score") or 0)

    co = skill_cooccurrence(
        db,
        days=days,
        min_support=_MIN_SUPPORT,
        country_code=country_code,
        lens=lens,
        query_ids=query_ids,
        min_evidence=min_evidence,
    )
    marginal: dict[str, int] = {}
    for row in co.get("items") or []:
        a, b = row.get("tech_a"), row.get("tech_b")
        fa = int(row.get("freq_a") or row.get("support") or 0)
        fb = int(row.get("freq_b") or row.get("support") or 0)
        if a:
            marginal[str(a)] = max(marginal.get(str(a), 0), fa)
        if b:
            marginal[str(b)] = max(marginal.get(str(b), 0), fb)

    trends = technology_trends(
        db,
        days=days,
        min_support=_MIN_SUPPORT,
        country_code=country_code,
        lens=lens,
        query_ids=query_ids,
        min_evidence=min_evidence,
    )
    rise_by_tech: dict[str, dict[str, Any]] = {}
    for t in trends.get("items") or []:
        name = t.get("technology")
        if name:
            rise_by_tech[str(name)] = {
                "status": t.get("status"),
                "growth_pct": t.get("growth_pct"),
                "sample_size": t.get("sample_size"),
            }

    best: dict[str, dict[str, Any]] = {}
    for row in co.get("items") or []:
        a, b = str(row.get("tech_a") or ""), str(row.get("tech_b") or "")
        if not a or not b:
            continue
        if a in owned and b not in owned:
            owned_anchor, adj = a, b
        elif b in owned and a not in owned:
            owned_anchor, adj = b, a
        else:
            continue
        support = int(row.get("support") or 0)
        lift = row.get("lift")
        prev = best.get(adj)
        if prev is None or support > int(prev.get("support") or 0):
            best[adj] = {
                "technology": adj,
                "anchor": owned_anchor,
                "support": support,
                "lift": lift,
            }

    max_support = max((int(v["support"]) for v in best.values()), default=1)
    max_marginal = max(marginal.values(), default=1)
    max_demand = max(demand_by_tech.values(), default=1.0)

    # Default gap weights (documented): demand / growth / rates / compatibility.
    w_demand = 0.40
    w_growth = 0.25
    w_rates = 0.15  # applied only when rate sample ok
    w_compat = 0.20

    candidates: list[dict[str, Any]] = []
    for adj, edge in best.items():
        demand_score = demand_by_tech.get(adj, 0.0)
        trend = rise_by_tech.get(adj) or {}
        growth = _growth_boost(trend.get("status"), trend.get("growth_pct"))
        comps = score_components_for_candidate(
            lift=edge.get("lift") if isinstance(edge.get("lift"), (int, float)) else None,
            support=int(edge["support"]),
            max_support=max_support,
            marginal_freq=marginal.get(adj, int(edge["support"])),
            max_marginal=max_marginal,
            demand_score=demand_score,
            max_demand=max_demand,
        )
        # Blend documented weights into final display score (keeps comps for UI).
        blended = round(
            w_demand * float(comps["demand_norm"])
            + w_growth * growth
            + w_compat * float(comps["complement"])
            + float(comps["irreplaceability_score"]) * 0.5
            - 0.1 * float(comps["generic_penalty"]),
            4,
        )
        candidates.append(
            {
                "technology": adj,
                "anchor_skill": edge["anchor"],
                "support": edge["support"],
                "lift": edge.get("lift"),
                "gap_priority": demand_score,
                "rise_cool_status": trend.get("status"),
                "growth_pct": trend.get("growth_pct"),
                "growth_component": round(growth, 4),
                "evidence_kind": "derived",
                "limits": [
                    "Co-occurrence and gap scores are observed mentions in the corpus, "
                    "not market size or earnings guarantee."
                ],
                "drilldown": {
                    "relations_seed": adj,
                    "relations_href": f"/relations?view=graph&seed={adj}",
                    "certifications_href": "/certifications",
                },
                "score": blended,
                "rate_check": None,
                **comps,
            }
        )

    for tech, dscore in demand_by_tech.items():
        if tech in owned or tech in best:
            continue
        trend = rise_by_tech.get(tech) or {}
        growth = _growth_boost(trend.get("status"), trend.get("growth_pct"))
        comps = score_components_for_candidate(
            lift=None,
            support=0,
            max_support=max_support,
            marginal_freq=marginal.get(tech, 0),
            max_marginal=max_marginal,
            demand_score=dscore,
            max_demand=max_demand,
        )
        blended = round(
            w_demand * float(comps["demand_norm"])
            + w_growth * growth
            + float(comps["irreplaceability_score"]) * 0.4,
            4,
        )
        candidates.append(
            {
                "technology": tech,
                "anchor_skill": None,
                "support": 0,
                "lift": None,
                "gap_priority": dscore,
                "rise_cool_status": trend.get("status"),
                "growth_pct": trend.get("growth_pct"),
                "growth_component": round(growth, 4),
                "evidence_kind": "derived",
                "limits": [
                    "Gap-only candidate (no co-occurrence edge above min_support). "
                    "Observed mentions only."
                ],
                "drilldown": {
                    "relations_seed": tech,
                    "relations_href": f"/relations?view=graph&seed={tech}",
                    "certifications_href": "/certifications",
                },
                "score": blended,
                "rate_check": None,
                **comps,
            }
        )

    candidates.sort(
        key=lambda c: (
            -float(c.get("score") or 0),
            -float(c.get("irreplaceability_score") or 0),
            -float(c.get("gap_priority") or 0),
        )
    )
    top = candidates[: max(1, min(int(top_n), 50))]

    if include_rates:
        for c in top[:8]:
            tech = str(c.get("technology") or "")
            if not tech:
                continue
            rate_payload = rate_for_technology(
                db,
                technology=tech,
                days=max(days, 180),
                country_code=country_code,
                lens=lens,
                query_ids=query_ids,
                min_evidence=min_evidence,
                min_sample=_RATE_N_MIN,
            )
            c["rate_check"] = rate_payload
            if rate_payload.get("status") == "ok" and rate_payload.get("rate"):
                # Soft boost when rate evidence exists (weight rates).
                c["score"] = round(float(c["score"]) + w_rates * 0.5, 4)
            elif rate_payload.get("status") == "insufficient_data":
                lim = c.get("limits") or []
                if isinstance(lim, list):
                    lim = list(lim) + [str(rate_payload.get("limits") or "Rate data thin.")]
                    c["limits"] = lim

    owned_certs = {
        c.strip().lower()
        for c in (owned_certifications or [])
        if c and str(c).strip()
    }
    related_certs: list[dict[str, Any]] = []
    try:
        certs = top_certifications(
            db,
            days=days,
            country_code=country_code,
            lens=lens if lens != "compare" else "market",
            query_ids=query_ids,
            top_n=15,
            min_evidence=min_evidence,
        )
        for item in certs.get("items") or []:
            display = str(item.get("certification") or item.get("display_name") or "").strip()
            slug = str(item.get("slug") or display).strip()
            if not slug and not display:
                continue
            if slug.lower() in owned_certs or display.lower() in owned_certs:
                continue
            related_certs.append(
                {
                    "slug": item.get("slug"),
                    "display_name": display,
                    "mentions": item.get("job_mentions") or item.get("mentions"),
                    "drilldown": {"certifications_href": "/certifications"},
                    "evidence_kind": "derived",
                    "limits": "Observed certification mentions in ads — not a ranking of value.",
                }
            )
            if len(related_certs) >= 8:
                break
    except Exception:  # noqa: BLE001 — empty DB / missing tables in unit CI
        related_certs = []

    return {
        "owned_skills": sorted(owned),
        "owned_certifications": sorted(
            c.strip()
            for c in (owned_certifications or [])
            if c and str(c).strip()
        ),
        "period_days": days,
        "lens": lens,
        "query_ids": list(query_ids) if query_ids else None,
        "countries": gaps_payload.get("countries"),
        "sample_size": co.get("jobs_analyzed")
        or gaps_payload.get("accessible_remote_b2b_jobs_observed"),
        "jobs_analyzed": co.get("jobs_analyzed"),
        "candidates": top,
        "related_certifications": related_certs,
        "score_version": STACK_COMPASS_SCORE_VERSION,
        "methodology_version": settings.methodology_version,
        "weights": {
            "demand": w_demand,
            "growth": w_growth,
            "rates": w_rates,
            "compatibility": w_compat,
        },
        "disclaimer": (
            "Learning candidates combine skill gaps and co-occurrence lift with an "
            "irreplaceability score. Observed corpus only — not a training ROI guarantee."
        ),
        "source": gaps_payload.get("source"),
        "gaps_top": (gaps_payload.get("gaps") or [])[:10],
    }


def learning_candidates(
    db: Session,
    *,
    owned_skills: list[str],
    days: int = 90,
    country_code: Optional[str] = None,
    lens: Optional[str] = None,
    query_ids: Optional[Sequence[int]] = None,
    min_evidence: Optional[str] = None,
    top_n: int = 15,
    owned_certifications: Optional[list[str]] = None,
    include_rates: bool = True,
) -> dict[str, Any]:
    lens_name = parse_lens(lens) if lens else None
    if lens_name == "compare":
        market = _learning_candidates_flat(
            db,
            owned_skills=owned_skills,
            days=days,
            country_code=country_code,
            lens="market",
            query_ids=query_ids,
            min_evidence=min_evidence,
            top_n=top_n,
            owned_certifications=owned_certifications,
            include_rates=include_rates,
        )
        focus = _learning_candidates_flat(
            db,
            owned_skills=owned_skills,
            days=days,
            country_code=country_code,
            lens="focus",
            query_ids=query_ids,
            min_evidence=min_evidence,
            top_n=top_n,
            owned_certifications=owned_certifications,
            include_rates=include_rates,
        )
        return {
            "lens": "compare",
            "query_ids": list(query_ids) if query_ids else None,
            "period_days": days,
            "score_version": STACK_COMPASS_SCORE_VERSION,
            "methodology_version": get_settings().methodology_version,
            **compare_counts(
                db, query_ids=query_ids, days=days, country_code=country_code
            ),
            "market": market,
            "focus": focus,
            "disclaimer": market.get("disclaimer"),
        }

    return _learning_candidates_flat(
        db,
        owned_skills=owned_skills,
        days=days,
        country_code=country_code,
        lens=lens,
        query_ids=query_ids,
        min_evidence=min_evidence,
        top_n=top_n,
        owned_certifications=owned_certifications,
        include_rates=include_rates,
    )

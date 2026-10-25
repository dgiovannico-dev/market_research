"""Evidence-coach brief handlers — call analytics; never invent KPIs."""

from __future__ import annotations

from typing import Any, Optional, Sequence

from sqlalchemy.orm import Session

from app.analytics import kpis
from app.analytics.countries import country_comparison
from app.analytics.rates import rate_explorer
from app.application.briefs.handlers_adjacent import adjacent, suggest_watches
from app.application.briefs.human_narrative import (
    focus_vs_market_narrative,
    normalize_locale,
    rising_cooling_narrative,
    where_demand_narrative,
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
    status_for_n,
    thin_or_refuse,
    with_evidence_limits,
)

__all__ = [
    "rising_cooling",
    "where_demand",
    "adjacent",
    "focus_vs_market",
    "suggest_watches",
]


def rising_cooling(
    db: Session,
    *,
    lens: str = DEFAULT_LENS,
    query_ids: Optional[Sequence[int]] = None,
    period_days: int = 90,
    country_code: Optional[str] = None,
    locale: str = "en",
) -> dict[str, Any]:
    """Wrap ``technology_trends`` half-period Δ (+ rates when present)."""
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
        "Observed technology mentions in stored jobs only; half-period growth "
        "is not causation. Rates excluded when undeclared."
    )
    refused = thin_or_refuse(
        brief_type="rising_cooling",
        lens=lens,
        sample_size=n,
        limits=limits,
        excluded_thin_n=excluded,
        extra=countries_extra(country_code),
        locale=loc,
    )
    if refused:
        return refused

    alens = flat_lens(lens)
    trends = kpis.technology_trends(
        db,
        days=period_days,
        min_support=MIN_SAMPLE,
        country_code=country_code,
        lens=alens,
        query_ids=query_ids,
    )
    rising = [
        t
        for t in trends.get("items", [])
        if t.get("status") == "ok" and (t.get("growth_pct") or 0) > 0
    ][:8]
    cooling = [
        t
        for t in trends.get("items", [])
        if t.get("status") == "ok" and (t.get("growth_pct") or 0) < 0
    ][:8]
    rates = rate_explorer(
        db,
        days=period_days,
        min_sample=MIN_SAMPLE,
        country_code=country_code,
        lens=alens,
        query_ids=query_ids,
    )
    rate_ok = [r for r in rates.get("items", []) if r.get("status") == "ok"][:5]

    evidence: list[dict[str, Any]] = [
        {
            "metric": "technology_trends",
            "period_days": trends.get("period_days"),
            "rising": rising,
            "cooling": cooling,
            "source": "kpis.technology_trends",
            "countries": trends.get("countries"),
        }
    ]
    if rate_ok:
        evidence.append(
            {
                "metric": "rates",
                "items": rate_ok,
                "source": "rate_explorer",
                "disclaimer": rates.get("disclaimer"),
            }
        )

    status = status_for_n(n)
    narrative = rising_cooling_narrative(
        locale=loc,
        lens=lens,
        n=n,
        period_days=period_days,
        rising=rising,
        cooling=cooling,
        rate_buckets=len(rate_ok),
        jobs_with_rates=int(rates.get("jobs_with_rates") or 0),
        thin=status == "thin_sample",
        thin_threshold=THIN_SAMPLE,
        geo=geo_label(country_code),
    )

    return base_payload(
        brief_type="rising_cooling",
        lens=lens,
        sample_size=n,
        evidence=evidence,
        narrative=narrative,
        limits=limits,
        status=status,
        excluded_thin_n=excluded,
        extra=countries_extra(country_code),
    )


def where_demand(
    db: Session,
    *,
    lens: str = DEFAULT_LENS,
    query_ids: Optional[Sequence[int]] = None,
    period_days: int = 90,
    country_code: Optional[str] = None,
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
        "Country/remote mix from observed country_code and remote_type only; "
        "not a census. Not legal/tax advice."
    )
    refused = thin_or_refuse(
        brief_type="where_demand",
        lens=lens,
        sample_size=n,
        limits=limits,
        excluded_thin_n=excluded,
        extra=countries_extra(country_code),
        locale=loc,
    )
    if refused:
        return refused

    alens = flat_lens(lens)
    geo = country_comparison(
        db,
        days=period_days,
        country_code=country_code,
        lens=alens,
        query_ids=query_ids,
    )
    items = sorted(
        geo.get("items", []), key=lambda x: x.get("jobs_observed", 0), reverse=True
    )[:12]
    evidence = [
        {
            "metric": "countries_breakdown",
            "period_days": geo.get("period_days"),
            "items": items,
            "source": "country_comparison",
            "disclaimer": geo.get("disclaimer"),
            "countries": geo.get("countries"),
        }
    ]
    status = status_for_n(n)
    narrative = where_demand_narrative(
        locale=loc,
        lens=lens,
        n=n,
        period_days=period_days,
        items=items,
        thin=status == "thin_sample",
        thin_threshold=THIN_SAMPLE,
        geo=geo_label(country_code),
    )
    return base_payload(
        brief_type="where_demand",
        lens=lens,
        sample_size=n,
        evidence=evidence,
        narrative=narrative,
        limits=limits,
        status=status,
        excluded_thin_n=excluded,
        extra=countries_extra(country_code),
    )


def focus_vs_market(
    db: Session,
    *,
    lens: str = "compare",
    query_ids: Optional[Sequence[int]] = None,
    period_days: int = 90,
    country_code: Optional[str] = None,
    locale: str = "en",
) -> dict[str, Any]:
    del lens
    lens = "compare"
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
        "Compare uses market vs focus job sets from job_intent_matches. "
        "Overlap jobs counted in both. Not total market size."
    )
    refused = thin_or_refuse(
        brief_type="focus_vs_market",
        lens=lens,
        sample_size=n,
        limits=limits,
        excluded_thin_n=excluded,
        extra=countries_extra(country_code),
        locale=loc,
    )
    if refused:
        return refused

    summary = kpis.dashboard_summary(
        db,
        days=period_days,
        lens="compare",
        query_ids=query_ids,
        country_code=country_code,
    )
    m_count = summary.get("market_n") or summary.get("market_job_count") or 0
    f_count = summary.get("focus_n") or summary.get("focus_job_count") or 0
    overlap = summary.get("overlap_n") or summary.get("overlap_job_count") or 0
    evidence = [
        {
            "metric": "dashboard_summary_compare",
            "market_job_count": m_count,
            "focus_job_count": f_count,
            "overlap_job_count": overlap,
            "market_kpis": (summary.get("market") or {}).get("kpis", [])[:6],
            "focus_kpis": (summary.get("focus") or {}).get("kpis", [])[:6],
            "source": "kpis.dashboard_summary",
            "countries": summary.get("countries"),
        }
    ]
    status = status_for_n(n)
    focus_thin = int(f_count) < MIN_SAMPLE
    if focus_thin:
        status = "thin_sample" if status == "ok" else status
    narrative = focus_vs_market_narrative(
        locale=loc,
        n=n,
        period_days=period_days,
        market_n=int(m_count),
        focus_n=int(f_count),
        overlap_n=int(overlap),
        focus_thin=focus_thin,
        min_sample=MIN_SAMPLE,
        thin=status == "thin_sample" and not focus_thin,
        thin_threshold=THIN_SAMPLE,
        geo=geo_label(country_code),
    )
    return base_payload(
        brief_type="focus_vs_market",
        lens=lens,
        sample_size=n,
        evidence=evidence,
        narrative=narrative,
        limits=limits,
        status=status,
        excluded_thin_n=excluded,
        extra=countries_extra(country_code),
    )

"""Skill co-occurrence via SQL pair aggregation (DSS)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Sequence

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session, aliased

from app.analytics.country_filter import parse_country_codes
from app.analytics.evidence_gate import (
    DEFAULT_MIN_EVIDENCE,
    count_thin_in_query,
    evidence_meta,
    parse_min_evidence,
)
from app.analytics.job_query import base_job_query
from app.analytics.lenses import compare_counts, parse_lens, resolve_job_id_subquery
from app.storage.models import Job, JobSkill, Technology


def skill_cooccurrence(
    db: Session,
    *,
    days: int = 90,
    min_support: int = 3,
    country_code: Optional[str] = None,
    lens: Optional[str] = None,
    query_ids: Optional[Sequence[int]] = None,
    min_evidence: Optional[str] = DEFAULT_MIN_EVIDENCE,
) -> dict[str, Any]:
    lens_name = parse_lens(lens)
    job_id_subq = resolve_job_id_subquery(db, lens_name, query_ids)
    codes = parse_country_codes(country_code)
    tier = parse_min_evidence(min_evidence)
    now = datetime.now(timezone.utc)
    date_from = now - timedelta(days=days)
    corpus_all = base_job_query(
        date_from=date_from,
        country_codes=codes,
        job_id_subq=job_id_subq,
        min_evidence=None,
    )
    excluded_thin_n = count_thin_in_query(db, corpus_all) if tier == "standard" else 0
    corpus = base_job_query(
        date_from=date_from,
        country_codes=codes,
        job_id_subq=job_id_subq,
        min_evidence=tier,
    )
    job_id_sub = corpus.with_only_columns(Job.id).subquery()
    job_ids = select(job_id_sub.c.id)
    n_jobs = int(db.scalar(select(func.count()).select_from(job_id_sub)) or 0)
    denom_jobs = n_jobs or 1

    js = aliased(JobSkill)
    freq_rows = db.execute(
        select(Technology.canonical_name, func.count(func.distinct(js.job_id)))
        .select_from(js)
        .join(Technology, Technology.id == js.technology_id)
        .where(js.job_id.in_(job_ids))
        .group_by(Technology.canonical_name)
    ).all()
    single = {name: int(cnt) for name, cnt in freq_rows}

    js_a = aliased(JobSkill)
    js_b = aliased(JobSkill)
    tech_a = aliased(Technology)
    tech_b = aliased(Technology)
    pair_rows = db.execute(
        select(
            tech_a.canonical_name,
            tech_b.canonical_name,
            func.count(func.distinct(js_a.job_id)),
        )
        .select_from(js_a)
        .join(
            js_b,
            and_(
                js_a.job_id == js_b.job_id,
                js_a.technology_id < js_b.technology_id,
            ),
        )
        .join(tech_a, tech_a.id == js_a.technology_id)
        .join(tech_b, tech_b.id == js_b.technology_id)
        .where(js_a.job_id.in_(job_ids))
        .group_by(tech_a.canonical_name, tech_b.canonical_name)
        .having(func.count(func.distinct(js_a.job_id)) >= min_support)
    ).all()

    items = []
    for a, b, count in pair_rows:
        count_i = int(count)
        p_a = single.get(a, 0) / denom_jobs
        p_b = single.get(b, 0) / denom_jobs
        p_ab = count_i / denom_jobs
        expected = p_a * p_b
        lift = (p_ab / expected) if expected > 0 else None
        j_denom = single.get(a, 0) + single.get(b, 0) - count_i
        jaccard = (count_i / j_denom) if j_denom else None
        items.append(
            {
                "tech_a": a,
                "tech_b": b,
                "support": count_i,
                "lift": round(lift, 3) if lift is not None else None,
                "jaccard": round(jaccard, 3) if jaccard is not None else None,
                "freq_a": single.get(a, 0),
                "freq_b": single.get(b, 0),
                "evidence_kind": "derived",
                "limits": "Co-occurrence is not causation. Sample limited to stored jobs.",
            }
        )
    items.sort(key=lambda x: (-x["support"], -(x["lift"] or 0)))
    out: dict[str, Any] = {
        "period_days": days,
        "min_support": min_support,
        "lens": lens_name,
        "query_ids": list(query_ids) if query_ids else None,
        "countries": codes or None,
        "jobs_analyzed": n_jobs,
        "items": items[:200],
        **evidence_meta(min_evidence=tier, excluded_thin_n=excluded_thin_n),
    }
    if lens_name == "compare":
        out.update(
            compare_counts(
                db, query_ids=query_ids, days=days, country_code=country_code
            )
        )
    return out


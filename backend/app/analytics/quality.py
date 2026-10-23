"""Data quality report (lens-aware) with per-source breakdown."""

from __future__ import annotations

from typing import Any, Optional, Sequence

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.analytics.country_filter import parse_country_codes
from app.analytics.job_query import base_job_query
from app.analytics.lenses import compare_counts, parse_lens, resolve_job_id_subquery
from app.storage.enums import EvidenceTier
from app.storage.models import Job, JobRate, Source


def data_quality_report(
    db: Session,
    *,
    country_code: Optional[str] = None,
    lens: str = "market",
    query_ids: Optional[Sequence[int]] = None,
) -> dict[str, Any]:
    lens_name = parse_lens(lens)
    job_id_subq = resolve_job_id_subquery(db, lens_name, query_ids)
    codes = parse_country_codes(country_code)
    # Quality stays full-corpus (no min_evidence gate) but excludes closed_stale.
    base = base_job_query(
        country_codes=codes,
        job_id_subq=job_id_subq,
        min_evidence=None,
    )
    total = db.scalar(select(func.count()).select_from(base.subquery())) or 0
    if total == 0:
        return {
            "total_canonical_jobs": 0,
            "lens": lens_name,
            "query_ids": list(query_ids) if query_ids else None,
            "countries": codes or None,
            "metrics": {},
            "by_source": [],
            "sources": [],
            "disclaimer": "No jobs ingested yet.",
        }

    def pct(n: int) -> float:
        return round((n / total) * 100.0, 2)

    with_date = (
        db.scalar(
            select(func.count()).select_from(base.where(Job.published_at.is_not(None)).subquery())
        )
        or 0
    )
    known_country = (
        db.scalar(
            select(func.count()).select_from(base.where(Job.country_code != "unknown").subquery())
        )
        or 0
    )
    known_contract = (
        db.scalar(
            select(func.count()).select_from(base.where(Job.contract_type != "unknown").subquery())
        )
        or 0
    )
    thin_n = (
        db.scalar(
            select(func.count()).select_from(
                base.where(Job.evidence_tier == EvidenceTier.thin.value).subquery()
            )
        )
        or 0
    )
    job_ids = select(base.with_only_columns(Job.id).subquery().c.id)
    with_rate = (
        db.scalar(
            select(func.count(func.distinct(JobRate.job_id))).where(JobRate.job_id.in_(job_ids))
        )
        or 0
    )
    duplicates = (
        db.scalar(select(func.count()).select_from(Job).where(Job.is_canonical.is_(False))) or 0
    )

    by_source_rows = db.execute(
        select(
            Job.source_id,
            func.count(Job.id),
            func.sum(case((Job.country_code != "unknown", 1), else_=0)),
            func.sum(case((Job.evidence_tier == EvidenceTier.thin.value, 1), else_=0)),
            func.max(Job.last_seen_at),
        )
        .where(Job.id.in_(job_ids))
        .group_by(Job.source_id)
    ).all()
    source_meta = {
        s.id: s
        for s in db.scalars(
            select(Source).where(Source.id.in_([r[0] for r in by_source_rows] or [-1]))
        ).all()
    }
    rate_by_source = {
        sid: n
        for sid, n in db.execute(
            select(Job.source_id, func.count(func.distinct(JobRate.job_id)))
            .select_from(JobRate)
            .join(Job, Job.id == JobRate.job_id)
            .where(Job.id.in_(job_ids))
            .group_by(Job.source_id)
        ).all()
    }
    by_source: list[dict[str, Any]] = []
    for sid, n, known_c, thin_c, last_seen in by_source_rows:
        src = source_meta.get(sid)
        n_i = int(n)
        by_source.append(
            {
                "source_id": sid,
                "name": src.name if src else None,
                "connector_type": src.connector_type if src else None,
                "n": n_i,
                "pct_known_country": round((int(known_c) / n_i) * 100.0, 2) if n_i else 0.0,
                "pct_thin": round((int(thin_c) / n_i) * 100.0, 2) if n_i else 0.0,
                "pct_with_rate": round((int(rate_by_source.get(sid, 0)) / n_i) * 100.0, 2)
                if n_i
                else 0.0,
                "last_seen_at": last_seen.isoformat() if last_seen else None,
            }
        )
    by_source.sort(key=lambda r: -r["n"])

    out: dict[str, Any] = {
        "total_canonical_jobs": total,
        "lens": lens_name,
        "query_ids": list(query_ids) if query_ids else None,
        "countries": codes or None,
        "metrics": {
            "pct_with_valid_date": pct(with_date),
            "pct_known_country": pct(known_country),
            "pct_known_contract": pct(known_contract),
            "pct_with_rate": pct(with_rate),
            "pct_thin": pct(thin_n),
            "thin_n": thin_n,
            "duplicate_non_canonical_count": duplicates,
        },
        "by_source": by_source,
        "sources": [
            {
                "id": s.id,
                "name": s.name,
                "connector_status": s.connector_status,
                "enabled": s.enabled,
                "last_success_at": s.last_success_at.isoformat() if s.last_success_at else None,
                "last_error": s.last_error,
                "coverage_notes": s.coverage_notes,
            }
            for s in db.scalars(select(Source)).all()
            if not (s.connector_type or "").startswith("dup_")
            and (s.connector_type or "")
            not in {"test", "fixture", "freework", "freelancermap"}
            and not (s.name or "").startswith(
                ("bf_src_", "dedup_empty_url_", "manual_empty", "clip-emp-")
            )
        ],
        "disclaimer": "Quality metrics describe this database, not the external market.",
    }
    if lens_name == "compare":
        out.update(compare_counts(db, query_ids=query_ids, country_code=country_code))
    return out

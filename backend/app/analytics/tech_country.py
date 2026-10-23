"""Technology × country matrix for correlative Relations dashboard."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.analytics.country_filter import parse_country_codes
from app.analytics.evidence_gate import (
    DEFAULT_MIN_EVIDENCE,
    count_thin_in_query,
    evidence_meta,
    parse_min_evidence,
)
from app.analytics.job_query import base_job_query
from app.analytics.lenses import parse_lens, resolve_job_id_subquery
from app.storage.models import Job, JobSkill, Technology

_MATRIX_LIMITS = (
    "Observed inventory only; cells below min_cell omitted."
)


def tech_country_matrix(
    db: Session,
    *,
    days: int = 30,
    country_code: Optional[str] = None,
    lens: Optional[str] = None,
    query_ids: Optional[Sequence[int]] = None,
    min_evidence: Optional[str] = DEFAULT_MIN_EVIDENCE,
    top_tech: int = 12,
    top_country: int = 10,
    min_cell: int = 2,
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
    sample_size = int(db.scalar(select(func.count()).select_from(job_id_sub)) or 0)

    if sample_size == 0:
        return {
            "period_days": days,
            "sample_size": 0,
            "technologies": [],
            "countries": [],
            "cells": [],
            **evidence_meta(min_evidence=tier, excluded_thin_n=excluded_thin_n),
            "limits": _MATRIX_LIMITS,
        }

    cell_rows = db.execute(
        select(
            Technology.canonical_name,
            Job.country_code,
            func.count(func.distinct(JobSkill.job_id)),
        )
        .select_from(JobSkill)
        .join(Technology, Technology.id == JobSkill.technology_id)
        .join(Job, Job.id == JobSkill.job_id)
        .where(JobSkill.job_id.in_(job_ids))
        .group_by(Technology.canonical_name, Job.country_code)
    ).all()

    tech_totals: dict[str, int] = defaultdict(int)
    country_totals: dict[str, int] = defaultdict(int)
    cells_raw: dict[tuple[str, str], int] = {}
    for tech, cc, cnt in cell_rows:
        if not tech:
            continue
        country = (cc or "unknown").strip() or "unknown"
        n = int(cnt)
        cells_raw[(tech, country)] = n
        tech_totals[tech] += n
        if country != "unknown":
            country_totals[country] += n

    technologies = [
        name
        for name, _ in sorted(tech_totals.items(), key=lambda x: (-x[1], x[0]))[
            : max(1, top_tech)
        ]
    ]
    countries = [
        name
        for name, _ in sorted(country_totals.items(), key=lambda x: (-x[1], x[0]))[
            : max(1, top_country)
        ]
    ]
    tech_set = set(technologies)
    country_set = set(countries)

    cells = [
        {"technology": tech, "country_code": cc, "jobs": n}
        for (tech, cc), n in sorted(
            cells_raw.items(),
            key=lambda x: (-x[1], x[0][0], x[0][1]),
        )
        if tech in tech_set and cc in country_set and n >= min_cell
    ]

    return {
        "period_days": days,
        "sample_size": sample_size,
        "technologies": technologies,
        "countries": countries,
        "cells": cells,
        **evidence_meta(min_evidence=tier, excluded_thin_n=excluded_thin_n),
        "limits": _MATRIX_LIMITS,
    }

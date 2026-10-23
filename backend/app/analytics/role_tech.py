"""Role family × technology matrix for correlative Relations dashboard."""

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
    "Observed inventory only; cells below min_cell omitted. "
    "Jobs without role_family excluded from axes."
)


def role_tech_matrix(
    db: Session,
    *,
    days: int = 30,
    country_code: Optional[str] = None,
    lens: Optional[str] = None,
    query_ids: Optional[Sequence[int]] = None,
    min_evidence: Optional[str] = DEFAULT_MIN_EVIDENCE,
    top_role: int = 12,
    top_tech: int = 12,
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
            "role_families": [],
            "technologies": [],
            "cells": [],
            **evidence_meta(min_evidence=tier, excluded_thin_n=excluded_thin_n),
            "limits": _MATRIX_LIMITS,
        }

    cell_rows = db.execute(
        select(
            Job.role_family,
            Technology.canonical_name,
            func.count(func.distinct(JobSkill.job_id)),
        )
        .select_from(JobSkill)
        .join(Technology, Technology.id == JobSkill.technology_id)
        .join(Job, Job.id == JobSkill.job_id)
        .where(JobSkill.job_id.in_(job_ids))
        .group_by(Job.role_family, Technology.canonical_name)
    ).all()

    role_totals: dict[str, int] = defaultdict(int)
    tech_totals: dict[str, int] = defaultdict(int)
    cells_raw: dict[tuple[str, str], int] = {}
    for role, tech, cnt in cell_rows:
        role_name = (role or "").strip()
        if not role_name:
            continue
        if not tech:
            continue
        n = int(cnt)
        cells_raw[(role_name, tech)] = n
        role_totals[role_name] += n
        tech_totals[tech] += n

    role_families = [
        name
        for name, _ in sorted(role_totals.items(), key=lambda x: (-x[1], x[0]))[
            : max(1, top_role)
        ]
    ]
    technologies = [
        name
        for name, _ in sorted(tech_totals.items(), key=lambda x: (-x[1], x[0]))[
            : max(1, top_tech)
        ]
    ]
    role_set = set(role_families)
    tech_set = set(technologies)

    cells = [
        {"role_family": role, "technology": tech, "jobs": n}
        for (role, tech), n in sorted(
            cells_raw.items(),
            key=lambda x: (-x[1], x[0][0], x[0][1]),
        )
        if role in role_set and tech in tech_set and n >= min_cell
    ]

    return {
        "period_days": days,
        "sample_size": sample_size,
        "role_families": role_families,
        "technologies": technologies,
        "cells": cells,
        **evidence_meta(min_evidence=tier, excluded_thin_n=excluded_thin_n),
        "limits": _MATRIX_LIMITS,
    }

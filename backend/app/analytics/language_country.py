"""Language × country matrix for correlative Relations dashboard."""

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
from app.storage.models import Job

_MATRIX_LIMITS = (
    "Observed inventory only; human languages (ISO 639-1) from "
    "language_requirements × country_code. Cells below min_cell omitted. "
    "Missing language_requirements means extraction found none."
)


def _normalize_lang_codes(raw: Any) -> list[str]:
    if not isinstance(raw, list):
        return []
    out: list[str] = []
    for item in raw:
        if not isinstance(item, str):
            continue
        code = item.strip().lower()[:8]
        if len(code) >= 2 and code.isalpha():
            out.append(code)
    return out


def language_country_matrix(
    db: Session,
    *,
    days: int = 30,
    country_code: Optional[str] = None,
    lens: Optional[str] = None,
    query_ids: Optional[Sequence[int]] = None,
    min_evidence: Optional[str] = DEFAULT_MIN_EVIDENCE,
    top_language: int = 12,
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
    sample_size = int(db.scalar(select(func.count()).select_from(job_id_sub)) or 0)

    if sample_size == 0:
        return {
            "period_days": days,
            "sample_size": 0,
            "languages": [],
            "countries": [],
            "cells": [],
            **evidence_meta(min_evidence=tier, excluded_thin_n=excluded_thin_n),
            "limits": _MATRIX_LIMITS,
        }

    rows = db.execute(
        select(Job.language_requirements, Job.country_code).where(
            Job.id.in_(select(job_id_sub.c.id))
        )
    ).all()

    lang_totals: dict[str, int] = defaultdict(int)
    country_totals: dict[str, int] = defaultdict(int)
    cells_raw: dict[tuple[str, str], int] = defaultdict(int)

    for raw_langs, cc in rows:
        langs = set(_normalize_lang_codes(raw_langs))
        if not langs:
            continue
        raw_cc = (cc or "").strip()
        if not raw_cc or raw_cc.lower() == "unknown":
            country = "unknown"
        else:
            country = raw_cc.upper()
        for lang in langs:
            cells_raw[(lang, country)] += 1
            lang_totals[lang] += 1
            if country != "unknown":
                country_totals[country] += 1

    languages = [
        name
        for name, _ in sorted(lang_totals.items(), key=lambda x: (-x[1], x[0]))[
            : max(1, top_language)
        ]
    ]
    countries = [
        name
        for name, _ in sorted(country_totals.items(), key=lambda x: (-x[1], x[0]))[
            : max(1, top_country)
        ]
    ]
    lang_set = set(languages)
    country_set = set(countries)

    cells = [
        {"language": lang, "country_code": cc, "jobs": n}
        for (lang, cc), n in sorted(
            cells_raw.items(),
            key=lambda x: (-x[1], x[0][0], x[0][1]),
        )
        if lang in lang_set and cc in country_set and n >= min_cell
    ]

    return {
        "period_days": days,
        "sample_size": sample_size,
        "languages": languages,
        "countries": countries,
        "cells": cells,
        **evidence_meta(min_evidence=tier, excluded_thin_n=excluded_thin_n),
        "limits": _MATRIX_LIMITS,
    }

"""ADEM Luxembourg skills-in-vacancies open data (CC0) — reference stats, not RawJob."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

LATEST_CSV_URL = (
    "https://download.data.public.lu/resources/skills-required-in-adem-job-vacancies/"
    "20261020-090239/datasc-skills-vacancies-2025-2026.csv"
)

FIELDS = (
    "vacancy_id",
    "skill",
    "skill_uri",
    "positions",
    "month",
    "year",
    "canton",
    "occupation_code",
    "occupation_label",
    "nace_code",
    "nace_label",
)


def _int_positions(raw: str) -> int:
    try:
        return max(0, int(raw.strip() or "0"))
    except ValueError:
        return 0


def summarize_csv(
    path: Path,
    *,
    nace_prefix: str | None = None,
    top_skills: int = 50,
) -> dict[str, Any]:
    skill_rows: Counter[str] = Counter()
    skill_positions: Counter[str] = Counter()
    vacancies_by_month: dict[str, set[str]] = defaultdict(set)
    rows_total = 0
    rows_skipped_nace = 0
    rows_empty_skill = 0

    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        missing = [f for f in FIELDS if f not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"Unexpected CSV header; missing columns: {missing}")

        for row in reader:
            if nace_prefix:
                code = (row.get("nace_code") or "").strip()
                if not code.startswith(nace_prefix):
                    rows_skipped_nace += 1
                    continue

            rows_total += 1
            vid = (row.get("vacancy_id") or "").strip()
            skill = (row.get("skill") or "").strip()
            pos = _int_positions(row.get("positions") or "0")
            month = (row.get("month") or "").strip()
            year = (row.get("year") or "").strip()

            if vid and year and month:
                vacancies_by_month[f"{year}-{month.zfill(2)}"].add(vid)

            if not skill:
                rows_empty_skill += 1
                continue

            skill_rows[skill] += 1
            skill_positions[skill] += pos if pos else 1

    def _top(counter: Counter[str], n: int) -> list[dict[str, Any]]:
        return [{"skill": k, "count": v} for k, v in counter.most_common(n)]

    return {
        "evidence_kind": "official_statistics_reference",
        "license": "CC0",
        "source": "adem_lu_skills_opendata",
        "provider": "adem",
        "country": "LU",
        "input_file": str(path.resolve()),
        "filters": {"nace_prefix": nace_prefix},
        "rows_read": rows_total,
        "rows_empty_skill": rows_empty_skill,
        "rows_skipped_nace": rows_skipped_nace,
        "distinct_vacancies": len({v for s in vacancies_by_month.values() for v in s}),
        "vacancies_by_month": {k: len(v) for k, v in sorted(vacancies_by_month.items())},
        "top_skills_by_row_count": _top(skill_rows, top_skills),
        "top_skills_by_positions_weight": _top(skill_positions, top_skills),
        "disclaimer": (
            "Skills inferred from ADEM transferred vacancies (ESCO). "
            "Not live job ads — do not mix into Countries KPI counts."
        ),
    }

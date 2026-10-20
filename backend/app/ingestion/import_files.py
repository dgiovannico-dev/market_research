from __future__ import annotations

import io
import json
from datetime import datetime, timezone
from typing import Any

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.collectors.base import RawJob
from app.ingestion.service import ingest_raw_jobs
from app.storage.models import Source

DEFAULT_COLUMN_MAP = {
    "title": ["title", "job_title", "role"],
    "url": ["url", "link", "canonical_url", "job_url"],
    "company": ["company", "company_name", "employer"],
    "description": ["description", "job_description", "body"],
    "location": ["location", "country", "city"],
    "published_at": ["published_at", "publication_date", "date"],
    "salary": ["salary", "rate", "compensation"],
    "source_job_id": ["source_job_id", "id", "external_id"],
    "job_type": ["job_type", "contract_type", "employment_type"],
    "tags": ["tags", "skills", "technologies"],
}


def _pick(row: dict[str, Any], keys: list[str]) -> Any:
    lower = {str(k).lower(): v for k, v in row.items()}
    for key in keys:
        if key in lower and pd.notna(lower[key]):
            return lower[key]
    return None


def _parse_dt(value: Any) -> datetime | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    ts = pd.to_datetime(value, utc=True, errors="coerce")
    if pd.isna(ts):
        return None
    return ts.to_pydatetime()


def dataframe_to_raw_jobs(df: pd.DataFrame, column_map: dict[str, list[str]] | None = None) -> list[RawJob]:
    mapping = column_map or DEFAULT_COLUMN_MAP
    jobs: list[RawJob] = []
    for idx, row in df.iterrows():
        data = row.to_dict()
        title = _pick(data, mapping["title"])
        if not title:
            continue
        url = str(_pick(data, mapping["url"]) or f"manual://row/{idx}")
        tags_raw = _pick(data, mapping["tags"])
        if isinstance(tags_raw, str):
            tags = [t.strip() for t in tags_raw.replace(";", ",").split(",") if t.strip()]
        elif isinstance(tags_raw, list):
            tags = [str(t) for t in tags_raw]
        else:
            tags = []
        source_job_id = str(_pick(data, mapping["source_job_id"]) or f"manual-{idx}")
        jobs.append(
            RawJob(
                source_job_id=source_job_id,
                url=url,
                title=str(title),
                company=str(_pick(data, mapping["company"]) or "") or None,
                description=str(_pick(data, mapping["description"]) or "") or None,
                location=str(_pick(data, mapping["location"]) or "") or None,
                published_at=_parse_dt(_pick(data, mapping["published_at"])) or datetime.now(timezone.utc),
                salary_text=str(_pick(data, mapping["salary"]) or "") or None,
                tags=tags,
                job_type=str(_pick(data, mapping["job_type"]) or "") or None,
            )
        )
    return jobs


def import_tabular(
    db: Session,
    *,
    content: bytes,
    filename: str,
    column_map: dict[str, list[str]] | None = None,
) -> dict[str, Any]:
    source = db.scalar(select(Source).where(Source.name == "Manual CSV/JSON/XLSX Import"))
    if not source:
        raise ValueError("Manual import source missing. Seed reference data first.")
    name = filename.lower()
    if name.endswith(".json"):
        payload = json.loads(content.decode("utf-8"))
        if isinstance(payload, dict) and "jobs" in payload:
            payload = payload["jobs"]
        df = pd.DataFrame(payload)
    elif name.endswith(".xlsx"):
        df = pd.read_excel(io.BytesIO(content))
    else:
        df = pd.read_csv(io.BytesIO(content))
    raw_jobs = dataframe_to_raw_jobs(df, column_map=column_map)
    stats = ingest_raw_jobs(
        db,
        source_id=source.id,
        raw_jobs=raw_jobs,
        collection_method="manual_import",
    )
    return {"filename": filename, "records_received": len(raw_jobs), **stats}

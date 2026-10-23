"""Jobicy remote jobs — free public API (attribution required; no paid key)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

import httpx

from app.collectors.base import BaseCollector, CollectorResult, RawJob

_MAX_PAGES = 2


def _as_str_list(value: object) -> list[str]:
    """Jobicy returns industry/type as list or scalar; normalize to flat strings."""
    if value is None:
        return []
    if isinstance(value, str):
        text = value.strip()
        return [text] if text else []
    if isinstance(value, (list, tuple)):
        out: list[str] = []
        for item in value:
            out.extend(_as_str_list(item))
        return out
    text = str(value).strip()
    return [text] if text else []


def _map_job(item: dict, errors: list[str]) -> RawJob | None:
    job_id = item.get("id")
    title = item.get("jobTitle") or "Untitled"
    url = item.get("url") or ""
    if not job_id or not url:
        return None
    pub = item.get("pubDate")
    published = datetime.now(timezone.utc)
    if pub:
        try:
            published = datetime.fromisoformat(str(pub).replace("Z", "+00:00"))
        except ValueError:
            errors.append(f"invalid pubDate for {job_id}")
    salary_bits = []
    if item.get("salaryMin") or item.get("salaryMax"):
        salary_bits.append(
            f"{item.get('salaryMin') or '?'}-{item.get('salaryMax') or '?'} "
            f"{item.get('salaryCurrency') or ''} / {item.get('salaryPeriod') or ''}".strip()
        )
    tags = (
        _as_str_list(item.get("jobIndustry"))
        + _as_str_list(item.get("jobLevel"))
        + _as_str_list(item.get("jobType"))
    )
    job_types = _as_str_list(item.get("jobType"))
    return RawJob(
        source_job_id=str(job_id),
        url=url,
        title=title,
        company=item.get("companyName"),
        description=item.get("jobDescription") or item.get("jobExcerpt"),
        location=item.get("jobGeo") or "Remote",
        published_at=published,
        salary_text=" ".join(salary_bits) or None,
        tags=tags,
        job_type=job_types[0] if job_types else None,
        remote_hint=True,
        raw=item,
    )


class JobicyCollector(BaseCollector):
    name = "Jobicy"
    source_key = "jobicy"
    collection_mode = "dump"
    base_url = "https://jobicy.com/api/v2/remote-jobs"

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        headers = {"User-Agent": "FMI-MarketIntel/1.0", "Accept": "application/json"}
        errors: list[str] = []
        records: list[RawJob] = []
        pages = 0
        cursor: str | None = None
        tag = (query or "").strip()

        async with httpx.AsyncClient(timeout=45.0, headers=headers) as client:
            while pages < _MAX_PAGES:
                params: dict[str, str | int] = {"count": 50}
                if tag:
                    params["tag"] = tag
                if cursor:
                    params["cursor"] = cursor
                try:
                    resp = await client.get(self.base_url, params=params)
                    resp.raise_for_status()
                    payload = resp.json() or {}
                except Exception as exc:  # noqa: BLE001
                    if pages == 0:
                        return CollectorResult(records=[], pages_scanned=1, errors=[str(exc)])
                    errors.append(str(exc))
                    break

                pages += 1
                for item in payload.get("jobs") or []:
                    if not isinstance(item, dict):
                        continue
                    mapped = _map_job(item, errors)
                    if mapped:
                        records.append(mapped)

                cursor = payload.get("nextCursor")
                if not cursor or not payload.get("hasMore"):
                    break

        return CollectorResult(records=records, pages_scanned=max(pages, 1), errors=errors)

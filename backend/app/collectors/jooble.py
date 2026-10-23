"""Jooble Job Search API — requires JOOBLE_API_KEY."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

import httpx

from app.collectors.base import (
    BaseCollector,
    CollectorResult,
    RawJob,
    is_blank_query,
    missing_query_result,
    simplify_query_for,
)
from app.core.config import get_settings
from app.secrets.resolve import credential_bundle


class JoobleCollector(BaseCollector):
    name = "Jooble"
    source_key = "jooble"
    collection_mode = "search"
    base_url = "https://jooble.org/api"

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        if is_blank_query(query):
            return missing_query_result()
        settings = get_settings()
        api_key = (credential_bundle("jooble").get("api_key") or "").strip()
        if not api_key:
            return CollectorResult(
                records=[],
                pages_scanned=0,
                errors=["JOOBLE_API_KEY is required"],
            )

        keywords = simplify_query_for(self, query or "")
        location = settings.jooble_location.strip()
        payload = {"keywords": keywords, "page": 1}
        if location:
            payload["location"] = location

        async with httpx.AsyncClient(timeout=45.0) as client:
            try:
                resp = await client.post(
                    f"{self.base_url}/{api_key}",
                    json=payload,
                    headers={"Content-Type": "application/json", "Accept": "application/json"},
                )
                if resp.status_code in (401, 403):
                    return CollectorResult(
                        records=[],
                        pages_scanned=1,
                        errors=[f"Jooble auth failed HTTP {resp.status_code}"],
                    )
                resp.raise_for_status()
                data = resp.json() or {}
            except Exception as exc:  # noqa: BLE001
                return CollectorResult(records=[], pages_scanned=1, errors=[str(exc)])

        jobs = data.get("jobs") or []
        records: list[RawJob] = []
        for item in jobs:
            job_id = item.get("id")
            if job_id is None:
                continue
            published = datetime.now(timezone.utc)
            updated = item.get("updated")
            if updated:
                try:
                    published = datetime.fromisoformat(str(updated).replace("Z", "+00:00"))
                except ValueError:
                    pass
            records.append(
                RawJob(
                    source_job_id=str(job_id),
                    url=item.get("link") or "",
                    title=item.get("title") or "Untitled",
                    company=item.get("company"),
                    description=item.get("snippet"),
                    location=item.get("location"),
                    published_at=published,
                    salary_text=item.get("salary"),
                    tags=[],
                    job_type=item.get("type"),
                    remote_hint=None,
                    raw=item if isinstance(item, dict) else {},
                )
            )
        return CollectorResult(records=records, pages_scanned=1, errors=[])

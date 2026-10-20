from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

import httpx

from app.collectors.base import BaseCollector, CollectorResult, RawJob


class ArbeitnowCollector(BaseCollector):
    name = "Arbeitnow"
    source_key = "arbeitnow"
    base_url = "https://www.arbeitnow.com/api/job-board-api"

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        errors: list[str] = []
        records: list[RawJob] = []
        async with httpx.AsyncClient(timeout=45.0) as client:
            try:
                resp = await client.get(self.base_url)
                resp.raise_for_status()
                payload = resp.json()
            except Exception as exc:  # noqa: BLE001
                return CollectorResult(records=[], pages_scanned=1, errors=[str(exc)])

        for item in payload.get("data", []):
            title = item.get("title") or "Untitled"
            if query and query.lower() not in f"{title} {' '.join(item.get('tags') or [])}".lower():
                continue
            created = item.get("created_at")
            published = None
            if isinstance(created, (int, float)):
                published = datetime.fromtimestamp(created, tz=timezone.utc)
            records.append(
                RawJob(
                    source_job_id=str(item.get("slug") or item.get("url")),
                    url=item.get("url") or "",
                    title=title,
                    company=item.get("company_name"),
                    description=item.get("description"),
                    location=item.get("location"),
                    published_at=published or datetime.now(timezone.utc),
                    tags=list(item.get("tags") or []),
                    job_type=",".join(item.get("job_types") or []),
                    remote_hint=bool(item.get("remote")),
                    raw=item,
                )
            )
        return CollectorResult(records=records, pages_scanned=1, errors=errors)

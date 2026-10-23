from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

import httpx

from app.collectors.base import BaseCollector, CollectorResult, RawJob

# API documents ?page=; each page is ~300 jobs. Cap to stay polite.
_MAX_PAGES = 3


class ArbeitnowCollector(BaseCollector):
    name = "Arbeitnow"
    source_key = "arbeitnow"
    collection_mode = "dump"
    base_url = "https://www.arbeitnow.com/api/job-board-api"

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        errors: list[str] = []
        records: list[RawJob] = []
        pages = 0
        q = (query or "").lower().strip()

        async with httpx.AsyncClient(timeout=45.0) as client:
            page = 1
            while page <= _MAX_PAGES:
                try:
                    resp = await client.get(self.base_url, params={"page": page})
                    resp.raise_for_status()
                    payload = resp.json()
                except Exception as exc:  # noqa: BLE001
                    if pages == 0:
                        return CollectorResult(records=[], pages_scanned=1, errors=[str(exc)])
                    errors.append(str(exc))
                    break

                pages += 1
                for item in payload.get("data") or []:
                    if not isinstance(item, dict):
                        continue
                    title = item.get("title") or "Untitled"
                    tags = list(item.get("tags") or [])
                    if q and q not in f"{title} {' '.join(tags)}".lower():
                        continue
                    created = item.get("created_at")
                    published = None
                    if isinstance(created, (int, float)):
                        published = datetime.fromtimestamp(created, tz=timezone.utc)
                    # employment_type column is varchar(64); joined job_types often exceed it.
                    job_types = [
                        str(t).strip()
                        for t in (item.get("job_types") or [])
                        if str(t).strip()
                    ]
                    job_type = ",".join(job_types)[:64] if job_types else None
                    sid = str(item.get("slug") or item.get("url") or "")[:255]
                    if not sid or not (item.get("url") or "").strip():
                        continue
                    records.append(
                        RawJob(
                            source_job_id=sid,
                            url=item.get("url") or "",
                            title=title,
                            company=item.get("company_name"),
                            description=item.get("description"),
                            location=item.get("location"),
                            published_at=published or datetime.now(timezone.utc),
                            tags=tags,
                            job_type=job_type,
                            remote_hint=bool(item.get("remote")),
                            raw=item,
                        )
                    )

                next_url = (payload.get("links") or {}).get("next")
                if not next_url:
                    break
                page += 1

        return CollectorResult(records=records, pages_scanned=max(pages, 1), errors=errors)

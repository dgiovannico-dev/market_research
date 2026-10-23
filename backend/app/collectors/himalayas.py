"""Himalayas remote jobs — free public jobs API (no key)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

import httpx

from app.collectors.base import BaseCollector, CollectorResult, RawJob
from app.core.config import get_settings


class HimalayasCollector(BaseCollector):
    name = "Himalayas"
    source_key = "himalayas"
    collection_mode = "dump"
    base_url = "https://himalayas.app/jobs/api"

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        settings = get_settings()
        limit = max(1, min(int(settings.himalayas_page_limit or 40), 100))
        headers = {"User-Agent": "FMI-MarketIntel/1.0", "Accept": "application/json"}
        errors: list[str] = []
        records: list[RawJob] = []
        q = (query or "").lower().strip()
        cursor: str | None = None
        pages = 0

        async with httpx.AsyncClient(timeout=45.0, headers=headers, follow_redirects=True) as client:
            while pages < 2:
                params: dict[str, str | int] = {"limit": limit}
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
                    title = item.get("title") or "Untitled"
                    desc = item.get("description") or item.get("excerpt") or ""
                    if q and q not in title.lower() and q not in desc.lower():
                        continue
                    guid = item.get("guid") or item.get("applicationLink")
                    url = item.get("applicationLink") or ""
                    if not guid or not url:
                        continue
                    pub = item.get("pubDate")
                    published = datetime.now(timezone.utc)
                    if pub is not None:
                        try:
                            if isinstance(pub, (int, float)) or (
                                isinstance(pub, str) and pub.strip().isdigit()
                            ):
                                published = datetime.fromtimestamp(float(pub), tz=timezone.utc)
                            else:
                                published = datetime.fromisoformat(
                                    str(pub).replace("Z", "+00:00")
                                )
                        except (TypeError, ValueError, OSError):
                            errors.append(f"invalid pubDate for {guid}")
                    loc_bits = item.get("locationRestrictions") or []
                    if isinstance(loc_bits, list):
                        location = ", ".join(str(x) for x in loc_bits) or "Remote"
                    else:
                        location = str(loc_bits) if loc_bits else "Remote"
                    salary = None
                    if item.get("minSalary") or item.get("maxSalary"):
                        salary = (
                            f"{item.get('minSalary') or '?'}-{item.get('maxSalary') or '?'} "
                            f"{item.get('currency') or ''} / {item.get('salaryPeriod') or ''}"
                        ).strip()
                    cats = item.get("categories") or []
                    tags = [str(c) for c in cats] if isinstance(cats, list) else []
                    records.append(
                        RawJob(
                            source_job_id=str(guid),
                            url=url,
                            title=title,
                            company=item.get("companyName"),
                            description=desc or None,
                            location=location,
                            published_at=published,
                            salary_text=salary,
                            tags=tags,
                            job_type=item.get("employmentType"),
                            remote_hint=True,
                            raw=item,
                        )
                    )
                cursor = payload.get("nextCursor")
                if not cursor:
                    break

        return CollectorResult(records=records, pages_scanned=max(pages, 1), errors=errors)

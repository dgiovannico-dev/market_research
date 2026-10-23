"""SmartRecruiters public company postings API (no key; per-company identifiers)."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Optional

import httpx

from app.collectors.base import BaseCollector, CollectorResult, RawJob
from app.core.config import get_settings

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def _split_csv(value: str) -> list[str]:
    return [p.strip() for p in value.split(",") if p.strip()]


def _slug(title: str) -> str:
    return _SLUG_RE.sub("-", (title or "").lower()).strip("-")[:80]


class SmartRecruitersCollector(BaseCollector):
    name = "SmartRecruiters Job Postings"
    source_key = "smartrecruiters"
    collection_mode = "dump"
    base_url = "https://api.smartrecruiters.com/v1/companies"

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        companies = _split_csv(get_settings().smartrecruiters_companies)
        if not companies:
            return CollectorResult(records=[], errors=["SMARTRECRUITERS_COMPANIES empty"])
        errors: list[str] = []
        records: list[RawJob] = []
        q = (query or "").lower().strip()
        headers = {"User-Agent": "FMI-MarketIntel/1.0", "Accept": "application/json"}

        async with httpx.AsyncClient(timeout=60.0, headers=headers) as client:
            for company in companies:
                offset = 0
                limit = 100
                pages_for_company = 0
                # Cap pages to keep ingest bounded (public boards can be huge).
                while pages_for_company < 2:
                    try:
                        resp = await client.get(
                            f"{self.base_url}/{company}/postings",
                            params={"limit": limit, "offset": offset},
                        )
                        resp.raise_for_status()
                        payload = resp.json() or {}
                    except Exception as exc:  # noqa: BLE001
                        errors.append(f"{company}: {exc}")
                        break
                    pages_for_company += 1
                    content = payload.get("content") or []
                    if not content:
                        break
                    for item in content:
                        title = item.get("name") or "Untitled"
                        if q and q not in title.lower():
                            continue
                        job_id = item.get("id")
                        if job_id is None:
                            continue
                        ident = (item.get("company") or {}).get("identifier") or company
                        url = (
                            item.get("postingUrl")
                            or f"https://jobs.smartrecruiters.com/{ident}/{job_id}-{_slug(title)}"
                        )
                        loc = item.get("location") or {}
                        location = loc.get("fullLocation") or loc.get("city")
                        if loc.get("remote"):
                            remote_hint = True
                        elif loc.get("hybrid"):
                            remote_hint = None
                        else:
                            remote_hint = False if location else None
                        pub = item.get("releasedDate")
                        published = datetime.now(timezone.utc)
                        if pub:
                            try:
                                published = datetime.fromisoformat(str(pub).replace("Z", "+00:00"))
                            except ValueError:
                                pass
                        desc = None
                        ad = item.get("defaultJobAd") or item.get("jobAd")
                        if isinstance(ad, dict):
                            sections = ad.get("sections") or {}
                            if isinstance(sections, dict):
                                parts = []
                                for sec in sections.values():
                                    if isinstance(sec, dict) and sec.get("text"):
                                        parts.append(str(sec["text"]))
                                desc = "\n".join(parts) or None
                        tags = [
                            t
                            for t in (
                                (item.get("department") or {}).get("label"),
                                (item.get("function") or {}).get("label"),
                                (item.get("experienceLevel") or {}).get("id"),
                            )
                            if t
                        ]
                        records.append(
                            RawJob(
                                source_job_id=f"{ident}:{job_id}",
                                url=url,
                                title=title,
                                company=ident,
                                description=desc,
                                location=location,
                                published_at=published,
                                tags=tags,
                                remote_hint=remote_hint,
                                raw=item,
                            )
                        )
                    total = int(payload.get("totalFound") or 0)
                    offset += limit
                    if offset >= total or len(content) < limit:
                        break

        return CollectorResult(records=records, pages_scanned=len(companies), errors=errors)

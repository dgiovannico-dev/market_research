"""Per-tenant public ATS board collectors (Greenhouse, Lever, Ashby, Personio)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

import httpx

from app.collectors.base import BaseCollector, CollectorResult, RawJob
from app.core.config import get_settings

# Bound ingest size when many tenants are configured
MAX_PER_TENANT = 40


def _split_csv(value: str) -> list[str]:
    return [p.strip() for p in value.split(",") if p.strip()]


class GreenhouseCollector(BaseCollector):
    name = "Greenhouse Job Boards"
    source_key = "greenhouse"
    collection_mode = "dump"
    base_url = "https://boards-api.greenhouse.io/v1/boards"

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        boards = _split_csv(get_settings().greenhouse_boards)
        if not boards:
            return CollectorResult(records=[], errors=["GREENHOUSE_BOARDS empty"])
        errors: list[str] = []
        records: list[RawJob] = []
        q = (query or "").lower().strip()
        headers = {"User-Agent": "FMI-MarketIntel/1.0", "Accept": "application/json"}
        # Omit content=true — listing payload is enough; keeps multi-board runs bounded
        async with httpx.AsyncClient(timeout=45.0, headers=headers) as client:
            for board in boards:
                matched = 0
                try:
                    resp = await client.get(f"{self.base_url}/{board}/jobs")
                    resp.raise_for_status()
                    jobs = (resp.json() or {}).get("jobs") or []
                except Exception as exc:  # noqa: BLE001
                    errors.append(f"{board}: {exc}")
                    continue
                for item in jobs:
                    if matched >= MAX_PER_TENANT:
                        break
                    title = item.get("title") or "Untitled"
                    if q and q not in title.lower():
                        continue
                    loc = (item.get("location") or {}).get("name")
                    pub = item.get("updated_at") or item.get("created_at")
                    published = datetime.now(timezone.utc)
                    if pub:
                        try:
                            published = datetime.fromisoformat(str(pub).replace("Z", "+00:00"))
                        except ValueError:
                            pass
                    records.append(
                        RawJob(
                            source_job_id=f"{board}:{item.get('id')}",
                            url=item.get("absolute_url") or "",
                            title=title,
                            company=board,
                            description=None,
                            location=loc,
                            published_at=published,
                            remote_hint=None,
                            raw={"id": item.get("id"), "title": title, "board": board},
                        )
                    )
                    matched += 1
        return CollectorResult(records=records, pages_scanned=len(boards), errors=errors)


class LeverCollector(BaseCollector):
    name = "Lever Postings"
    source_key = "lever"
    collection_mode = "dump"
    base_url = "https://api.lever.co/v0/postings"

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        sites = _split_csv(get_settings().lever_sites)
        if not sites:
            return CollectorResult(records=[], errors=["LEVER_SITES empty"])
        errors: list[str] = []
        records: list[RawJob] = []
        q = (query or "").lower().strip()
        headers = {"User-Agent": "FMI-MarketIntel/1.0", "Accept": "application/json"}
        async with httpx.AsyncClient(timeout=60.0, headers=headers) as client:
            for site in sites:
                matched = 0
                try:
                    resp = await client.get(f"{self.base_url}/{site}", params={"mode": "json"})
                    resp.raise_for_status()
                    jobs = resp.json() or []
                except Exception as exc:  # noqa: BLE001
                    errors.append(f"{site}: {exc}")
                    continue
                if not isinstance(jobs, list):
                    errors.append(f"{site}: unexpected payload")
                    continue
                for item in jobs:
                    if matched >= MAX_PER_TENANT:
                        break
                    title = item.get("text") or "Untitled"
                    if q and q not in title.lower():
                        continue
                    cats = item.get("categories") or {}
                    location = cats.get("location")
                    created = item.get("createdAt")
                    published = datetime.now(timezone.utc)
                    if created:
                        try:
                            published = datetime.fromtimestamp(created / 1000, tz=timezone.utc)
                        except (TypeError, ValueError, OSError):
                            pass
                    desc = item.get("descriptionPlain") or item.get("description")
                    records.append(
                        RawJob(
                            source_job_id=f"{site}:{item.get('id')}",
                            url=item.get("hostedUrl") or item.get("applyUrl") or "",
                            title=title,
                            company=site,
                            description=desc if isinstance(desc, str) else None,
                            location=location,
                            published_at=published,
                            tags=[v for v in (cats.get("commitment"), cats.get("team")) if v],
                            raw={"id": item.get("id"), "text": title, "site": site},
                        )
                    )
                    matched += 1
        return CollectorResult(records=records, pages_scanned=len(sites), errors=errors)


class AshbyCollector(BaseCollector):
    name = "Ashby Job Boards"
    source_key = "ashby"
    collection_mode = "dump"
    base_url = "https://api.ashbyhq.com/posting-api/job-board"

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        orgs = _split_csv(get_settings().ashby_orgs)
        if not orgs:
            return CollectorResult(records=[], errors=["ASHBY_ORGS empty"])
        errors: list[str] = []
        records: list[RawJob] = []
        q = (query or "").lower().strip()
        headers = {"User-Agent": "FMI-MarketIntel/1.0", "Accept": "application/json"}
        async with httpx.AsyncClient(timeout=90.0, headers=headers) as client:
            for org in orgs:
                matched = 0
                try:
                    resp = await client.get(f"{self.base_url}/{org}")
                    resp.raise_for_status()
                    jobs = (resp.json() or {}).get("jobs") or []
                except Exception as exc:  # noqa: BLE001
                    errors.append(f"{org}: {exc}")
                    continue
                for item in jobs:
                    if matched >= MAX_PER_TENANT:
                        break
                    title = item.get("title") or "Untitled"
                    if q and q not in title.lower():
                        continue
                    loc = item.get("location")
                    if isinstance(loc, dict):
                        loc = loc.get("name")
                    records.append(
                        RawJob(
                            source_job_id=f"{org}:{item.get('id')}",
                            url=item.get("jobUrl") or item.get("applyUrl") or "",
                            title=title,
                            company=org,
                            description=item.get("descriptionPlain") or item.get("descriptionHtml"),
                            location=loc if isinstance(loc, str) else None,
                            published_at=datetime.now(timezone.utc),
                            raw={"id": item.get("id"), "title": title, "org": org},
                        )
                    )
                    matched += 1
        return CollectorResult(records=records, pages_scanned=len(orgs), errors=errors)


def _personio_job_url(company: str, job_id: int | str) -> str:
    return f"https://{company}.jobs.personio.de/job/{job_id}?language=en"


class PersonioCollector(BaseCollector):
    name = "Personio Career Boards"
    source_key = "personio"
    collection_mode = "dump"
    base_host = "jobs.personio.de"

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        companies = _split_csv(get_settings().personio_companies)
        if not companies:
            return CollectorResult(records=[], errors=["PERSONIO_COMPANIES empty"])
        errors: list[str] = []
        records: list[RawJob] = []
        q = (query or "").lower().strip()
        headers = {"User-Agent": "FMI-MarketIntel/1.0", "Accept": "application/json"}
        async with httpx.AsyncClient(timeout=60.0, headers=headers) as client:
            for company in companies:
                matched = 0
                try:
                    resp = await client.get(
                        f"https://{company}.{self.base_host}/search.json"
                    )
                    resp.raise_for_status()
                    payload = resp.json()
                except Exception as exc:  # noqa: BLE001
                    errors.append(f"{company}: {exc}")
                    continue
                if not isinstance(payload, list):
                    errors.append(f"{company}: unexpected payload")
                    continue
                if not payload:
                    errors.append(f"{company}: empty board")
                    continue
                for item in payload:
                    if matched >= MAX_PER_TENANT:
                        break
                    if not isinstance(item, dict):
                        continue
                    title = item.get("name") or "Untitled"
                    keywords = item.get("keywords") or ""
                    haystack = f"{title} {keywords}".lower()
                    if q and q not in haystack:
                        continue
                    job_id = item.get("id")
                    if job_id is None:
                        continue
                    office = item.get("office")
                    if not office and item.get("offices"):
                        offices = item.get("offices")
                        if isinstance(offices, list) and offices:
                            office = offices[0]
                    desc = item.get("description")
                    company_label = item.get("subcompany") or company
                    dept = item.get("department")
                    tags = [t.strip() for t in str(keywords).split(",") if t.strip()][:8]
                    if dept:
                        tags.insert(0, str(dept))
                    records.append(
                        RawJob(
                            source_job_id=f"{company}:{job_id}",
                            url=_personio_job_url(company, job_id),
                            title=title,
                            company=company_label if isinstance(company_label, str) else company,
                            description=desc if isinstance(desc, str) and desc.strip() else None,
                            location=office if isinstance(office, str) else None,
                            published_at=datetime.now(timezone.utc),
                            tags=tags or None,
                            raw={
                                "id": job_id,
                                "name": title,
                                "company_slug": company,
                                "employment_type": item.get("employment_type"),
                            },
                        )
                    )
                    matched += 1
        return CollectorResult(records=records, pages_scanned=len(companies), errors=errors)

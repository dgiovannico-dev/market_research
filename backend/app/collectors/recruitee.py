"""Recruitee public Careers Site offers API (per-slug allowlist; keyless until 2027-02-10)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

import httpx

from app.collectors.base import BaseCollector, CollectorResult, RawJob
from app.core.config import get_settings

MAX_PER_TENANT = 40


def _split_csv(value: str) -> list[str]:
    return [p.strip() for p in value.split(",") if p.strip()]


def _parse_published(value: Any) -> datetime:
    published = datetime.now(timezone.utc)
    if not value:
        return published
    text = str(value).strip()
    # e.g. "2026-10-15 09:31:36 UTC"
    if text.endswith(" UTC"):
        text = text[: -len(" UTC")].strip() + "+00:00"
        text = text.replace(" ", "T", 1)
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return published


def _location(item: dict[str, Any]) -> str | None:
    city = item.get("city")
    country = item.get("country") or item.get("country_code")
    loc = item.get("location")
    if isinstance(loc, str) and loc.strip():
        return loc.strip()
    parts = [str(p) for p in (city, country) if p]
    if parts:
        return ", ".join(parts)
    locs = item.get("locations")
    if isinstance(locs, list) and locs:
        first = locs[0]
        if isinstance(first, dict):
            name = first.get("city") or first.get("name")
            cc = first.get("country") or first.get("country_code")
            chunk = ", ".join(str(p) for p in (name, cc) if p)
            return chunk or None
    return None


def _remote_hint(item: dict[str, Any]) -> bool | None:
    if item.get("remote") is True:
        return True
    if item.get("on_site") is True and item.get("remote") is not True:
        return False
    if item.get("hybrid") is True:
        return None
    return None


class RecruiteeCollector(BaseCollector):
    name = "Recruitee Careers Offers"
    source_key = "recruitee"
    collection_mode = "dump"
    base_url_tmpl = "https://{slug}.recruitee.com/api/offers/"

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        slugs = [s.lower() for s in _split_csv(get_settings().recruitee_slugs)]
        if not slugs:
            return CollectorResult(records=[], errors=["RECRUITEE_SLUGS empty"])
        errors: list[str] = []
        records: list[RawJob] = []
        q = (query or "").lower().strip()
        headers = {"User-Agent": "FMI-MarketIntel/1.0", "Accept": "application/json"}

        async with httpx.AsyncClient(timeout=45.0, headers=headers, follow_redirects=True) as client:
            for slug in slugs:
                matched = 0
                try:
                    resp = await client.get(self.base_url_tmpl.format(slug=slug))
                    resp.raise_for_status()
                    payload = resp.json() or {}
                except Exception as exc:  # noqa: BLE001
                    errors.append(f"{slug}: {exc}")
                    continue
                offers = payload.get("offers") if isinstance(payload, dict) else payload
                if not isinstance(offers, list):
                    errors.append(f"{slug}: unexpected payload")
                    continue
                for item in offers:
                    if matched >= MAX_PER_TENANT:
                        break
                    if not isinstance(item, dict):
                        continue
                    title = item.get("title") or item.get("sharing_title") or "Untitled"
                    if q and q not in title.lower():
                        continue
                    job_id = item.get("id")
                    if job_id is None:
                        continue
                    url = item.get("careers_url") or ""
                    if not url and item.get("slug"):
                        url = f"https://{slug}.recruitee.com/o/{item['slug']}"
                    company = item.get("company_name") or slug
                    desc = item.get("description")
                    if not (isinstance(desc, str) and desc.strip()):
                        desc = item.get("requirements")
                    tags = []
                    if item.get("department"):
                        tags.append(str(item["department"]))
                    extra = item.get("tags")
                    if isinstance(extra, list):
                        tags.extend(str(t) for t in extra if t)
                    elif isinstance(extra, str) and extra.strip():
                        tags.append(extra.strip())
                    records.append(
                        RawJob(
                            source_job_id=f"{slug}:{job_id}",
                            url=url,
                            title=title,
                            company=company,
                            description=desc if isinstance(desc, str) and desc.strip() else None,
                            location=_location(item),
                            published_at=_parse_published(item.get("published_at") or item.get("created_at")),
                            tags=tags[:12],
                            remote_hint=_remote_hint(item),
                            raw={
                                "id": job_id,
                                "slug": item.get("slug"),
                                "title": title,
                                "company_slug": slug,
                            },
                        )
                    )
                    matched += 1

        return CollectorResult(records=records, pages_scanned=len(slugs), errors=errors)

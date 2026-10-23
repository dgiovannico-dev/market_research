"""Reed.co.uk — free public RSS by default; optional REED_API_KEY for JSON search API."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Any, Optional

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

_TAG_RE = re.compile(r"<[^>]+>")
RSS_URL = "https://www.reed.co.uk/jobs/rss"
API_URL = "https://www.reed.co.uk/api/1.0/search"


class ReedCollector(BaseCollector):
    name = "Reed"
    source_key = "reed"
    # Public default is RSS (feed). API key path still requires a query.
    collection_mode = "feed"
    base_url = RSS_URL

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        settings = get_settings()
        api_key = settings.reed_api_key.strip()
        if api_key:
            if is_blank_query(query):
                return missing_query_result()
            return await _collect_api(api_key, simplify_query_for(self, query or ""))
        # RSS: optional keywords soft-filter; blank → no invented topic.
        keywords = (
            simplify_query_for(self, query or "") if not is_blank_query(query) else ""
        )
        return await _collect_rss(keywords)


async def _collect_rss(keywords: str) -> CollectorResult:
    headers = {
        "User-Agent": "FMI-MarketIntel/1.0",
        "Accept": "application/rss+xml, application/xml, text/xml",
    }
    params = {"keywords": keywords} if keywords else None
    errors: list[str] = []
    try:
        async with httpx.AsyncClient(timeout=45.0, headers=headers) as client:
            resp = await client.get(RSS_URL, params=params)
            resp.raise_for_status()
            root = ET.fromstring(resp.content)
    except Exception as exc:  # noqa: BLE001
        return CollectorResult(records=[], pages_scanned=1, errors=[str(exc)])

    records: list[RawJob] = []
    for item in root.findall("./channel/item"):
        title = (item.findtext("title") or "Untitled").strip()
        link = (item.findtext("link") or "").strip()
        if link.startswith("http://"):
            link = "https://" + link[len("http://") :]
        guid = (item.findtext("guid") or link or title).strip()
        desc = item.findtext("description") or ""
        published = _parse_updated(item)
        salary_text = _salary_from_desc(desc)
        records.append(
            RawJob(
                source_job_id=str(guid),
                url=link,
                title=title,
                company=None,
                description=_TAG_RE.sub(" ", desc).strip() or None,
                location="UK",
                published_at=published,
                salary_text=salary_text,
                tags=[],
                job_type=None,
                remote_hint=None,
                raw={"title": title, "link": link, "mode": "rss"},
            )
        )
    return CollectorResult(records=records, pages_scanned=1, errors=errors)


async def _collect_api(api_key: str, keywords: str) -> CollectorResult:
    params = {
        "keywords": keywords,
        "resultsToTake": 50,
        "resultsToSkip": 0,
    }
    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.get(
                API_URL,
                params=params,
                auth=(api_key, ""),
                headers={"Accept": "application/json", "User-Agent": "FMI-MarketIntel/1.0"},
            )
            if resp.status_code in (401, 403):
                return CollectorResult(
                    records=[],
                    pages_scanned=1,
                    errors=[f"Reed auth failed HTTP {resp.status_code}"],
                )
            resp.raise_for_status()
            payload = resp.json()
    except Exception as exc:  # noqa: BLE001
        return CollectorResult(records=[], pages_scanned=1, errors=[str(exc)])

    results = (payload or {}).get("results") or []
    records: list[RawJob] = []
    for item in results:
        if not isinstance(item, dict):
            continue
        job_id = item.get("jobId")
        if job_id is None:
            continue
        loc_parts = [item.get("locationName"), item.get("county"), item.get("country")]
        location = ", ".join(p for p in loc_parts if p)
        published = datetime.now(timezone.utc)
        date_str = item.get("date")
        if date_str:
            try:
                published = datetime.fromisoformat(str(date_str).replace("Z", "+00:00"))
            except ValueError:
                pass
        salary_bits = []
        if item.get("minimumSalary") is not None:
            salary_bits.append(str(item.get("minimumSalary")))
        if item.get("maximumSalary") is not None:
            salary_bits.append(str(item.get("maximumSalary")))
        currency = item.get("currency") or "GBP"
        salary_text = f"{' - '.join(salary_bits)} {currency}" if salary_bits else None
        raw: dict[str, Any] = dict(item)
        raw["mode"] = "api"
        records.append(
            RawJob(
                source_job_id=str(job_id),
                url=item.get("jobUrl") or "",
                title=item.get("jobTitle") or "Untitled",
                company=item.get("employerName"),
                description=item.get("jobDescription"),
                location=location or None,
                published_at=published,
                salary_text=salary_text,
                tags=[],
                job_type=item.get("contractType"),
                remote_hint=None,
                raw=raw,
            )
        )
    return CollectorResult(records=records, pages_scanned=1, errors=[])


def _parse_updated(item: ET.Element) -> datetime:
    # Atom-style updated under RSS namespace variants
    for el in item:
        tag = el.tag.split("}")[-1]
        if tag == "updated" and el.text:
            try:
                return datetime.fromisoformat(el.text.replace("Z", "+00:00"))
            except ValueError:
                break
    return datetime.now(timezone.utc)


def _salary_from_desc(desc: str) -> str | None:
    text = _TAG_RE.sub(" ", desc)
    # Common Reed blurb: "Salary : Up to 70k" / "£45,000 - £55,000"
    m = re.search(
        r"(?:Salary\s*:\s*)?([£€$]\s?[\d,]+(?:\s*[-–]\s*[£€$]?\s?[\d,]+)?(?:\s*(?:k|K))?)",
        text,
        re.I,
    )
    if m:
        return m.group(1).strip()
    return None

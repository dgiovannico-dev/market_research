"""Robert Half — official public joblist XML syndication (no scrape).

Feeds: https://joblist.roberthalf.com/IZ/general_rh-{cc}.xml
Schema: JobPositionPosting (IZJobPositionPosting.xsd). Keyless Amazon S3/CloudFront.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Optional
from xml.etree.ElementTree import Element

import httpx

from app.collectors.base import BaseCollector, CollectorResult, RawJob
from app.core.config import get_settings

_TAG_RE = re.compile(r"<[^>]+>")
_FEED = "https://joblist.roberthalf.com/IZ/general_rh-{cc}.xml"
# Default: CH (small) + UK (large). Override via ROBERT_HALF_COUNTRIES CSV.
_DEFAULT_COUNTRIES = ("ch", "uk")


class RobertHalfCollector(BaseCollector):
    name = "Robert Half"
    source_key = "robert_half"
    collection_mode = "dump"
    base_url = "https://joblist.roberthalf.com/IZ/"

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        del query  # dump: full configured feeds
        settings = get_settings()
        raw = (settings.robert_half_countries or "").strip()
        countries = [
            c.strip().lower()
            for c in (raw.split(",") if raw else _DEFAULT_COUNTRIES)
            if c.strip()
        ]
        if not countries:
            countries = list(_DEFAULT_COUNTRIES)

        headers = {
            "User-Agent": "FMI-MarketIntel/1.0 (+market_research; robert-half-xml)",
            "Accept": "application/xml, text/xml, */*",
        }
        records: list[RawJob] = []
        errors: list[str] = []
        pages = 0
        all_ok = True

        async with httpx.AsyncClient(timeout=120.0, headers=headers, follow_redirects=True) as client:
            for cc in countries:
                url = _FEED.format(cc=cc)
                pages += 1
                try:
                    resp = await client.get(url)
                    if resp.status_code != 200:
                        all_ok = False
                        errors.append(f"{cc}: HTTP {resp.status_code}")
                        continue
                    root = ET.fromstring(resp.content)
                except Exception as exc:  # noqa: BLE001
                    all_ok = False
                    errors.append(f"{cc}: {exc}")
                    continue

                for posting in root.findall(".//JobPositionPosting"):
                    job = _parse_posting(posting, cc)
                    if job:
                        records.append(job)

        return CollectorResult(
            records=records,
            pages_scanned=pages,
            errors=errors,
            dump_complete=all_ok and bool(records),
            meta={"countries": countries, "feed_base": self.base_url},
        )


def _node_text(node: Element | None) -> str:
    if node is None:
        return ""
    direct = (node.text or "").strip()
    if direct:
        return direct
    return "".join(node.itertext()).strip()


def _first(el: Element, *tags: str) -> str:
    for tag in tags:
        node = el.find(f".//{tag}")
        text = _node_text(node)
        if text:
            return text
    return ""


def _parse_posting(posting: Element, country: str) -> RawJob | None:
    job_id = _first(posting, "JobPositionPostingId")
    title = _first(posting, "JobPositionTitle")
    if not job_id or not title:
        return None

    company = _first(posting, "HiringOrgName") or "Robert Half"
    website = _first(posting, "WebSite")
    desc_html = _first(posting, "FullDescription", "ShortDescription")
    desc = _TAG_RE.sub(" ", desc_html).strip() or None

    city = _first(posting, "Location")
    region = _first(posting, "Region")
    cc = _first(posting, "CountryCode") or country.upper()
    loc_parts = [p for p in (city, region, cc) if p]
    location = ", ".join(loc_parts) if loc_parts else country.upper()

    url = _first(posting, "URL")
    if not url.startswith("http"):
        url = website or f"https://www.roberthalf.com/jobs/{job_id}"

    published = _parse_date(_first(posting, "JobPositionPostDate"))
    job_type = _first(posting, "JobTypeCode", "JobType") or None
    sal_min = _first(posting, "SalaryMinimum")
    sal_max = _first(posting, "SalaryMaximum")
    sal_cur = _first(posting, "SalaryCurrency")
    sal_period = _first(posting, "SalaryPeriod")
    salary = None
    if sal_min or sal_max:
        salary = " ".join(
            p for p in (sal_cur, sal_min, "-", sal_max, sal_period) if p
        ).strip(" -")

    return RawJob(
        source_job_id=f"rh-{country}-{job_id}",
        url=url,
        title=title,
        company=company,
        description=desc,
        location=location,
        published_at=published,
        salary_text=salary or None,
        tags=[],
        job_type=job_type,
        remote_hint=None,
        raw={"country": country, "job_id": job_id, "feed": "IZ"},
    )


def _parse_date(raw: str) -> datetime | None:
    raw = (raw or "").strip()
    if not raw:
        return None
    for fmt in ("%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(raw, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None

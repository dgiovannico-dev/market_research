"""Canada Job Bank — ESDC open-data monthly CSV (Open Government Licence).

Dataset: https://open.canada.ca/data/dataset/ea639e28-c0fc-48bf-b5dd-b8899bd43072
CKAN package_show resolves the latest English ``all-job-postings`` TSV (UTF-16).
WIC snapshot IDs are point-in-time; live ``/jobposting/{id}`` pages often 410.
Canonical URL = Job Bank search deep-link (title + province). No HTML scrape.
"""

from __future__ import annotations

import csv
import io
from datetime import datetime, timezone
from typing import Any, Optional
from urllib.parse import quote_plus

import httpx

from app.collectors.base import BaseCollector, CollectorResult, RawJob, simplify_query_for

CKAN_PACKAGE_URL = (
    "https://open.canada.ca/data/api/3/action/package_show"
    "?id=ea639e28-c0fc-48bf-b5dd-b8899bd43072"
)
DATASET_PAGE = (
    "https://open.canada.ca/data/en/dataset/ea639e28-c0fc-48bf-b5dd-b8899bd43072"
)
SEARCH_URL = "https://www.jobbank.gc.ca/jobsearch/jobsearch"
USER_AGENT = "FMI-MarketIntel/1.0 (+market_research; OGL-Canada open-data ingest)"

MAX_RECORDS = 200
MAX_BYTES = 55_000_000

IT_TITLE_KEYWORDS = (
    "software",
    "developer",
    "programmer",
    "devops",
    "data scientist",
    "data engineer",
    "machine learning",
    "cyber",
    "web developer",
    "systems analyst",
    "full stack",
    "fullstack",
    "frontend",
    "backend",
    "qa engineer",
    "site reliability",
    "cloud engineer",
    "network technician",
    "user support technician",
    "computer network",
)


def _is_it_row(row: dict[str, str], query: str) -> bool:
    title = (row.get("Job Title") or "").lower()
    noc = (row.get("NOC21 Code") or "").strip()
    noc_name = (row.get("NOC21 Code Name") or "").lower()
    blob = f"{title} {noc_name}"
    if query and query not in blob and query not in noc:
        return False
    if noc.startswith("212") or noc.startswith("2222") or noc.startswith("20012"):
        return True
    if noc.startswith("21311"):
        return True
    return any(k in blob for k in IT_TITLE_KEYWORDS)


def _parse_date(raw: str | None) -> datetime:
    if raw and raw not in {"NA", ""}:
        for fmt in ("%Y/%m/%d", "%Y-%m-%d"):
            try:
                return datetime.strptime(raw.strip(), fmt).replace(tzinfo=timezone.utc)
            except ValueError:
                continue
    return datetime.now(timezone.utc)


def _salary(row: dict[str, str]) -> str | None:
    lo = (row.get("Salary Minimum") or "").strip()
    hi = (row.get("Salary Maximum") or "").strip()
    per = (row.get("Salary Per") or "").strip()
    if lo in {"", "NA"} and hi in {"", "NA"}:
        return None
    parts = [p for p in (lo if lo != "NA" else None, hi if hi != "NA" else None) if p]
    if not parts:
        return None
    band = "-".join(parts) if len(parts) > 1 else parts[0]
    unit = f" CAD/{per}" if per and per != "NA" else " CAD"
    return f"{band}{unit}"


def _location(row: dict[str, str]) -> str:
    bits: list[str] = []
    city = (row.get("City") or "").strip()
    prov = (row.get("Province/Territory") or "").strip()
    if city and city != "NA":
        bits.append(city)
    if prov and prov != "NA":
        bits.append(prov)
    bits.append("CA")
    return ", ".join(bits)


def _search_url(title: str, province: str, snap: str) -> str:
    """Job Bank search deep-link; ``fmi_snap`` keeps canonical_url unique per row."""
    q = quote_plus(title.strip())
    loc = quote_plus(province.strip()) if province and province != "NA" else ""
    base = f"{SEARCH_URL}?searchstring={q}"
    if loc:
        base = f"{base}&locationstring={loc}"
    return f"{base}&fmi_snap={quote_plus(snap)}"


def _map_row(row: dict[str, str]) -> RawJob | None:
    snap = (row.get("WIC Job Location Snapshot ID") or "").strip()
    title = (row.get("Job Title") or "").strip()
    if not snap or not title:
        return None
    prov = (row.get("Province/Territory") or "").strip()
    tele = (row.get("Employment Term Telework") or "").strip().lower()
    remote: bool | None = None
    if tele == "yes":
        remote = True
    elif tele == "no":
        remote = False
    tags = [
        t
        for t in (
            row.get("NOC21 Code"),
            row.get("Employment Type"),
            row.get("Employment Term"),
            row.get("Official Language"),
        )
        if t and t != "NA"
    ]
    noc_name = (row.get("NOC21 Code Name") or "").strip()
    # Unique description avoids cross-row description_hash dedup (shared NOC names).
    desc = f"{noc_name} — {title} ({prov or 'CA'}; snap {snap})".strip(" —")
    return RawJob(
        source_job_id=snap,
        url=_search_url(title, prov, snap),
        title=title,
        company=None,
        description=desc,
        location=_location(row),
        published_at=_parse_date(row.get("First Posting Date")),
        salary_text=_salary(row),
        tags=tags[:10],
        job_type=row.get("Employment Type") if row.get("Employment Type") != "NA" else None,
        remote_hint=remote,
        raw={
            "country": "CA",
            "country_code": "CA",
            "evidence_tier": "thin",
            "noc21": row.get("NOC21 Code"),
            "province": prov,
            "dataset": DATASET_PAGE,
            "licence": "OGL-Canada",
            "mode": "open_data_csv",
        },
    )


def _ckan_resource_meta(res: dict[str, Any], package_id: Any) -> dict[str, Any]:
    meta: dict[str, Any] = {
        "name": res.get("name"),
        "url": str(res.get("url") or ""),
        "package_id": package_id,
    }
    if res.get("last_modified"):
        meta["last_modified"] = res["last_modified"]
    if res.get("created"):
        meta["created"] = res["created"]
    return meta


def _is_en_csv_resource(res: dict[str, Any]) -> bool:
    url = str(res.get("url") or "")
    name = str(res.get("name") or "").lower()
    if "job-bank-open-data-all-job-postings-en-" in url:
        return True
    if "all-job-postings-en-" in url or (
        "all job postings" in name and "english" in name
    ):
        return bool(url.endswith(".csv") or "download/" in url)
    return False


async def _latest_en_csv_resource(
    client: httpx.AsyncClient,
) -> dict[str, Any] | None:
    """Resolve EN all-job-postings CSV resource metadata from CKAN package_show."""
    try:
        resp = await client.get(CKAN_PACKAGE_URL)
        resp.raise_for_status()
        payload = resp.json() or {}
    except Exception:  # noqa: BLE001
        return None
    result = payload.get("result") or {}
    package_id = result.get("id")
    resources = result.get("resources") or []
    if not isinstance(resources, list):
        return None
    for res in resources:
        if isinstance(res, dict) and _is_en_csv_resource(res):
            return _ckan_resource_meta(res, package_id)
    return None


class JobBankCaCollector(BaseCollector):
    name = "Canada Job Bank (open data)"
    source_key = "jobbank_ca"
    collection_mode = "dump"
    base_url = DATASET_PAGE

    async def collect(self, query: Optional[str] = None) -> CollectorResult:
        q = simplify_query_for(self, query or "").lower()
        headers = {"User-Agent": USER_AGENT, "Accept": "*/*"}
        errors: list[str] = []

        async with httpx.AsyncClient(
            timeout=httpx.Timeout(180.0, connect=30.0),
            headers=headers,
            follow_redirects=True,
        ) as client:
            ckan = await _latest_en_csv_resource(client)
            csv_url = (ckan or {}).get("url") if ckan else None
            if not csv_url:
                return CollectorResult(
                    records=[], pages_scanned=1, errors=["ckan: no EN CSV resource"]
                )
            try:
                resp = await client.get(csv_url)
                resp.raise_for_status()
                raw = resp.content
            except Exception as exc:  # noqa: BLE001
                return CollectorResult(
                    records=[], pages_scanned=1, errors=[f"csv download: {exc}"]
                )

        if len(raw) > MAX_BYTES:
            errors.append(f"csv_too_large:{len(raw)}")
            raw = raw[:MAX_BYTES]

        try:
            text = raw.decode("utf-16")
        except UnicodeError:
            try:
                text = raw.decode("utf-8-sig")
            except UnicodeError as exc:
                return CollectorResult(
                    records=[], pages_scanned=1, errors=[f"decode: {exc}"]
                )

        candidates: list[RawJob] = []
        seen: set[str] = set()
        reader = csv.DictReader(io.StringIO(text), delimiter="\t")
        for row in reader:
            if not isinstance(row, dict):
                continue
            if not _is_it_row(row, q):
                continue
            mapped = _map_row(row)
            if mapped is None or mapped.source_job_id in seen:
                continue
            seen.add(mapped.source_job_id)
            candidates.append(mapped)

        # Prefer freshest postings when the open-data dump is capped.
        _epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
        candidates.sort(
            key=lambda j: j.published_at or _epoch,
            reverse=True,
        )
        records = candidates[:MAX_RECORDS]

        if not records:
            errors.append("no_it_rows_matched")

        meta = {
            "source": self.source_key,
            "ckan": ckan,
            "records": len(records),
            "mode": "open_data_csv",
        }
        return CollectorResult(
            records=records, pages_scanned=1, errors=errors, meta=meta
        )

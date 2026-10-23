"""Canada Job Bank open-data collector — mocked CKAN + CSV (no network)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.collectors.jobbank_ca import JobBankCaCollector
from app.collectors.registry import COLLECTOR_GEO, COLLECTORS


def _utf16_tsv() -> bytes:
    header = (
        "WIC Job Location Snapshot ID\tJob Title\tOriginal Job Title\t"
        "NOC 2016 Code\tNOC 2016 Code Name\tNOC21 Code\tNOC21 Code Name\t"
        "External Indicator\tFirst Posting Date\tVacancy Count\t"
        "Official Language\tEducation LOS\tExperience Level\tGovernment Type\t"
        "Placement Agency\tNAICS\tProvince/Territory\tCity\t"
        "Work Location Postal Code\tEconomic  Region\tVarious Location\t"
        "Employment Type\tEmployment Term\tEmployment Term Start Date\t"
        "Employment Term End Date\tEmployment Term Oncall\t"
        "Employment Term Overtime\tEmployment Term Day\tEmployment Term Evening\t"
        "Employment Term Shift\tEmployment Term Weekend\tEmployment Term Night\t"
        "Employment Term Telework\tEmployment Term Early\tEmployment Term Flex\t"
        "Employment Term Morning\tEmployment Term TBD\tSalary Condition Detail\t"
        "Salary Per\tSalary Minimum\tSalary Maximum\t"
        "Salary Condition Collective\tSalary Condition Bonus\t"
        "Salary Condition Disability\tSalary Condition Gratuity\t"
        "Salary Condition Medical\tSalary Condition Mileage\t"
        "Salary Condition Piecework\tSalary Condition Commission\t"
        "Salary Condition RESP\tSalary Condition Dental\t"
        "Salary Condition Group Insurance\tSalary Condition Life Insurance\t"
        "Salary Condition Pension\tSalary Condition RRSP\tCondition Vision Care\t"
        "Salary Condition Other Benefits\tCommission PER\tCommission Type\t"
        "Hours Per\tHours Minimum\tHours Maximum\tWork Hours\t"
        "Work Hours From Time\tWork Hours To Time"
    )
    # Minimal columns the mapper reads — DictReader tolerates shorter rows via restval
    short_header = (
        "WIC Job Location Snapshot ID\tJob Title\tNOC21 Code\tNOC21 Code Name\t"
        "First Posting Date\tProvince/Territory\tCity\tEmployment Type\t"
        "Employment Term\tOfficial Language\tEmployment Term Telework\t"
        "Salary Per\tSalary Minimum\tSalary Maximum"
    )
    row_it = (
        "15886796\tsoftware developer\t21232\tSoftware developers and programmers\t"
        "2026/09/18\tBritish Columbia\tVancouver\tFull-time\tPermanent\tEnglish\tYes\t"
        "Hour\t50\t80"
    )
    row_cook = (
        "1\tlicensed cook\t63200\tCooks\t2026/09/01\tAlberta\tCalgary\tFull-time\t"
        "Permanent\tEnglish\tNo\tYear\t40000\t50000"
    )
    text = "\n".join([short_header, row_it, row_cook]) + "\n"
    return text.encode("utf-16")


@pytest.mark.asyncio
async def test_jobbank_ca_filters_it_and_tags_ca():
    csv_bytes = _utf16_tsv()
    csv_url = (
        "https://open.canada.ca/data/dataset/x/resource/y/"
        "download/job-bank-open-data-all-job-postings-en-sept2026.csv"
    )
    ckan = {
        "result": {
            "id": "ea639e28-c0fc-48bf-b5dd-b8899bd43072",
            "resources": [
                {
                    "name": "September 2026 EN",
                    "url": csv_url,
                    "last_modified": "2026-09-15T12:00:00",
                    "created": "2026-09-01T00:00:00",
                }
            ]
        }
    }

    mock_client = AsyncMock()
    ckan_resp = MagicMock()
    ckan_resp.raise_for_status = MagicMock()
    ckan_resp.json.return_value = ckan
    csv_resp = MagicMock()
    csv_resp.raise_for_status = MagicMock()
    csv_resp.content = csv_bytes
    mock_client.get = AsyncMock(side_effect=[ckan_resp, csv_resp])
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("app.collectors.jobbank_ca.httpx.AsyncClient", return_value=mock_client):
        result = await JobBankCaCollector().collect()

    assert result.errors == []
    assert len(result.records) == 1
    job = result.records[0]
    assert job.title == "software developer"
    assert job.raw.get("country_code") == "CA"
    assert job.raw.get("evidence_tier") == "thin"
    assert "jobbank.gc.ca" in job.url
    assert "fmi_snap=15886796" in job.url
    assert "British" in (job.location or "")
    assert result.meta["source"] == "jobbank_ca"
    assert result.meta["mode"] == "open_data_csv"
    assert result.meta["records"] == 1
    assert result.meta["ckan"] == {
        "name": "September 2026 EN",
        "url": csv_url,
        "package_id": "ea639e28-c0fc-48bf-b5dd-b8899bd43072",
        "last_modified": "2026-09-15T12:00:00",
        "created": "2026-09-01T00:00:00",
    }


@pytest.mark.asyncio
async def test_jobbank_ca_prefers_freshest_before_cap():
    short_header = (
        "WIC Job Location Snapshot ID\tJob Title\tNOC21 Code\tNOC21 Code Name\t"
        "First Posting Date\tProvince/Territory\tCity\tEmployment Type\t"
        "Employment Term\tOfficial Language\tEmployment Term Telework\t"
        "Salary Per\tSalary Minimum\tSalary Maximum"
    )
    older = (
        "100\tsoftware developer\t21232\tSoftware developers and programmers\t"
        "2026/01/01\tOntario\tToronto\tFull-time\tPermanent\tEnglish\tYes\t"
        "Hour\t40\t60"
    )
    newer = (
        "200\tpython developer\t21232\tSoftware developers and programmers\t"
        "2026/09/30\tOntario\tOttawa\tFull-time\tPermanent\tEnglish\tYes\t"
        "Hour\t50\t70"
    )
    text = "\n".join([short_header, older, newer]) + "\n"
    csv_bytes = text.encode("utf-16")
    ckan = {
        "result": {
            "resources": [
                {
                    "url": (
                        "https://example.com/job-bank-open-data-all-job-postings-en-x.csv"
                    )
                }
            ]
        }
    }
    mock_client = AsyncMock()
    ckan_resp = MagicMock()
    ckan_resp.raise_for_status = MagicMock()
    ckan_resp.json.return_value = ckan
    csv_resp = MagicMock()
    csv_resp.raise_for_status = MagicMock()
    csv_resp.content = csv_bytes
    mock_client.get = AsyncMock(side_effect=[ckan_resp, csv_resp])
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with (
        patch("app.collectors.jobbank_ca.MAX_RECORDS", 1),
        patch("app.collectors.jobbank_ca.httpx.AsyncClient", return_value=mock_client),
    ):
        result = await JobBankCaCollector().collect()

    assert len(result.records) == 1
    assert result.records[0].source_job_id.endswith("200") or "200" in result.records[0].url
    assert result.records[0].title == "python developer"


@pytest.mark.asyncio
async def test_jobbank_ca_query_filters():
    csv_bytes = _utf16_tsv()
    ckan = {
        "result": {
            "resources": [
                {
                    "url": (
                        "https://example.com/job-bank-open-data-all-job-postings-en-x.csv"
                    )
                }
            ]
        }
    }
    mock_client = AsyncMock()
    ckan_resp = MagicMock()
    ckan_resp.raise_for_status = MagicMock()
    ckan_resp.json.return_value = ckan
    csv_resp = MagicMock()
    csv_resp.raise_for_status = MagicMock()
    csv_resp.content = csv_bytes
    mock_client.get = AsyncMock(side_effect=[ckan_resp, csv_resp])
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("app.collectors.jobbank_ca.httpx.AsyncClient", return_value=mock_client):
        result = await JobBankCaCollector().collect(query="nurse")

    assert result.records == []


def test_jobbank_ca_registered():
    assert "jobbank_ca" in COLLECTORS
    assert COLLECTORS["jobbank_ca"].collection_mode == "dump"
    assert "CA" in COLLECTOR_GEO["jobbank_ca"]

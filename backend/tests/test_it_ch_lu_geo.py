"""IT/CH/LU coverage corrections (geo affinity + Eurostat OJA allowlist)."""

from __future__ import annotations

import pytest

from app.collectors.registry import COLLECTOR_GEO, COLLECTORS
from app.core.config import get_settings
from app.stats.eurostat import ALLOWED_DATASETS, fetch_eurostat_series


def test_infojobs_geo_is_spain_not_italy():
    assert COLLECTORS["infojobs"].source_key == "infojobs"
    assert COLLECTOR_GEO["infojobs"] == frozenset({"ES"})
    assert "IT" not in COLLECTOR_GEO["infojobs"]


def test_adzuna_geo_includes_it_and_ch():
    geo = COLLECTOR_GEO["adzuna"]
    assert {"IT", "CH", "GB"} <= geo
    assert "LU" not in geo  # Adzuna does not support Luxembourg


def test_ats_collectors_have_it_ch_lu_affinity():
    for key in ("ashby", "lever", "smartrecruiters", "workday", "workable", "pinpoint"):
        assert key in COLLECTORS
        assert {"IT", "CH", "LU"} & COLLECTOR_GEO[key]


def test_ats_defaults_include_it_ch_lu_tenants():
    """Probed green boards (2026-10-22/23) stay in Settings defaults."""
    s = get_settings()
    gh = {x.strip() for x in s.greenhouse_boards.split(",") if x.strip()}
    ash = {x.strip() for x in s.ashby_orgs.split(",") if x.strip()}
    wd = {x.strip() for x in s.workday_tenants.split(",") if x.strip()}
    assert {"thefork", "truelayer"} <= gh
    assert {"satispay", "docebo"} <= ash
    assert "swisscom:wd103:SwisscomExternalCareers" in wd
    assert "juliusbaer:wd3:External" in wd
    assert "moneyfarm" in {x.strip() for x in s.workable_slugs.split(",") if x.strip()}
    assert "musixmatch" in {x.strip() for x in s.lever_sites.split(",") if x.strip()}
    assert {"Talan", "Devoteam"} <= {
        x.strip() for x in s.smartrecruiters_companies.split(",") if x.strip()
    }


def test_eurostat_oja_datasets_allowlisted():
    assert "isoc_sk_oja" in ALLOWED_DATASETS
    assert "isoc_sk_oja2" in ALLOWED_DATASETS


@pytest.mark.asyncio
async def test_eurostat_oja2_italy_live():
    result = await fetch_eurostat_series("isoc_sk_oja2", geo="IT", time=None, limit=5)
    if result.get("error") and not result.get("items"):
        pytest.skip(f"eurostat unavailable: {result.get('error')}")
    assert result["provider"] == "eurostat"
    assert result["dataset"] == "isoc_sk_oja2"
    assert result["geo"] == "IT"
    assert result["total_values"] >= 1

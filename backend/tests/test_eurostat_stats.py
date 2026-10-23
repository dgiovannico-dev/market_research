from __future__ import annotations

from typing import get_args

import pytest

from app.api.v1.stats import EurostatDataset
from app.stats.eurostat import ALLOWED_DATASETS, fetch_eurostat_series


def test_eurostat_api_literal_matches_allowlist():
    assert frozenset(get_args(EurostatDataset)) == ALLOWED_DATASETS


@pytest.mark.asyncio
async def test_eurostat_hourly_earnings_live():
    result = await fetch_eurostat_series("earn_ses_hourly", geo="DE", time="2022", limit=5)
    if result.get("error") and not result.get("items"):
        pytest.skip(f"eurostat unavailable: {result.get('error')}")
    assert result["provider"] == "eurostat"
    assert result["evidence_kind"] == "official_statistics_reference"
    assert result["total_values"] >= 1
    assert len(result["items"]) >= 1


@pytest.mark.asyncio
async def test_eurostat_rejects_unknown_dataset():
    result = await fetch_eurostat_series("not_a_real_dataset")
    assert result["items"] == []
    assert "allowlisted" in (result.get("error") or "")


@pytest.mark.asyncio
async def test_eurostat_oja_allowlisted_not_error_for_unknown():
    """isoc_sk_oja2 must pass the allowlist gate (may still fail network)."""
    result = await fetch_eurostat_series("isoc_sk_oja2", geo="IT", time=None, limit=3)
    assert "allowlisted" not in (result.get("error") or "")
    assert result["dataset"] == "isoc_sk_oja2"

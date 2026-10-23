from __future__ import annotations

import pytest

from app.taxonomy.esco import search_esco


@pytest.mark.asyncio
async def test_esco_search_occupations_live():
    result = await search_esco("software engineer", type_="occupation", limit=3)
    if result.get("error") and not result.get("items"):
        pytest.skip(f"esco unavailable: {result.get('error')}")
    assert result["provider"] == "esco"
    assert result["evidence_kind"] == "taxonomy_reference"
    assert len(result["items"]) >= 1
    assert result["items"][0].get("title")
    assert result["items"][0].get("uri")


@pytest.mark.asyncio
async def test_esco_empty_query():
    result = await search_esco("")
    assert result["items"] == []
    assert result.get("error") == "empty_query"

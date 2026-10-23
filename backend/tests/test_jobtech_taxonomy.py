from __future__ import annotations

import pytest

from app.taxonomy.jobtech import search_jobtech


@pytest.mark.asyncio
async def test_jobtech_search_skills_live():
    result = await search_jobtech("python", type_="skill", limit=5)
    if result.get("error") and not result.get("items"):
        pytest.skip(f"jobtech unavailable: {result.get('error')}")
    assert result["provider"] == "jobtech"
    assert result["evidence_kind"] == "taxonomy_reference"
    assert len(result["items"]) >= 1
    assert result["items"][0].get("title")
    assert result["items"][0].get("code")


@pytest.mark.asyncio
async def test_jobtech_empty_query():
    result = await search_jobtech("")
    assert result["items"] == []
    assert result.get("error") == "empty_query"

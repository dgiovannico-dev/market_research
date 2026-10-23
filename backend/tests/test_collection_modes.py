"""CollectionMode annotations + search collectors reject blank queries."""

from __future__ import annotations

import pytest

from app.collectors.base import MISSING_QUERY
from app.collectors.registry import COLLECTORS, VALID_COLLECTION_MODES, get_collection_mode

# DEFAULT_QUERY / Settings topic regression lives in test_collection_mode.py


def test_every_collector_has_valid_collection_mode():
    assert COLLECTORS, "expected registered collectors"
    for key, collector in COLLECTORS.items():
        mode = get_collection_mode(collector)
        assert mode in VALID_COLLECTION_MODES, f"{key}: invalid collection_mode={mode!r}"
        # Prefer explicit class attr (BaseCollector default alone is not enough signal).
        on_class = "collection_mode" in type(collector).__dict__
        assert on_class, f"{key}: collection_mode must be set on the collector class"


@pytest.mark.asyncio
async def test_search_collectors_reject_blank_query():
    search = {
        key: c for key, c in COLLECTORS.items() if get_collection_mode(c) == "search"
    }
    assert search, "expected at least one search-mode collector"

    for key, collector in search.items():
        for blank in (None, "", "   "):
            result = await collector.collect(blank)
            assert result.records == [], f"{key} collect({blank!r}) must return no records"
            assert any(
                MISSING_QUERY in err for err in result.errors
            ), f"{key} collect({blank!r}) errors must contain {MISSING_QUERY!r}, got {result.errors!r}"

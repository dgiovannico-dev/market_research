"""Wave 8: market_queries facades preserve evidence defaults."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from app.analytics.evidence_gate import DEFAULT_MIN_EVIDENCE
from app.application.market_queries import technology_trends
from app.bootstrap import build_container, reset_container
from app.core.config import get_settings


def test_technology_trends_default_min_evidence_is_standard():
    db = MagicMock()
    with patch(
        "app.application.market_queries.kpis._kpis.technology_trends",
        return_value={"items": []},
    ) as mocked:
        technology_trends(db, days=90)
        kwargs = mocked.call_args.kwargs
        assert kwargs["min_evidence"] == DEFAULT_MIN_EVIDENCE == "standard"


def test_container_exposes_external_stats():
    reset_container()
    c = build_container(get_settings())
    assert hasattr(c.external_stats, "eurostat_datasets")
    summary = c.external_stats.eurostat_datasets()
    assert summary["provider"] == "eurostat"
    assert "datasets" in summary
    reset_container()

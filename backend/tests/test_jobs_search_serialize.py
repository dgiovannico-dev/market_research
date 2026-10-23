"""Unit tests for research job serialization."""

from __future__ import annotations

from types import SimpleNamespace

from app.research.jobs_search import _serialize_job


def test_serialize_job_includes_evidence_tier():
    job = SimpleNamespace(
        id=1,
        title_original="Dev",
        company_original="Co",
        source=SimpleNamespace(name="src"),
        source_id=2,
        country_code="IT",
        published_at=None,
        contract_type="freelance",
        remote_type="remote",
        seniority=None,
        status="active",
        evidence_tier="thin",
        canonical_url="https://example.com/j/1",
        skills=[],
        rates=[],
    )
    out = _serialize_job(job)  # type: ignore[arg-type]
    assert out["evidence_tier"] == "thin"
    assert out["status"] == "active"

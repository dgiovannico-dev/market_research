"""evidence_tier resolution for DSS quality gates."""

from datetime import datetime, timezone

from app.collectors.base import RawJob
from app.ingestion.evidence_tier import resolve_evidence_tier, source_snapshot_at_from_raw


def _raw(**kwargs) -> RawJob:
    defaults = {
        "source_job_id": "1",
        "url": "https://example.com/j/1",
        "title": "Dev",
        "description": "Full body text about Python.",
        "raw": {},
    }
    defaults.update(kwargs)
    return RawJob(**defaults)


def test_explicit_thin_tag_wins():
    assert (
        resolve_evidence_tier(
            _raw(description="has text", raw={"evidence_tier": "thin"})
        )
        == "thin"
    )


def test_explicit_standard_tag():
    assert (
        resolve_evidence_tier(_raw(description=None, raw={"evidence_tier": "standard"}))
        == "standard"
    )


def test_empty_description_is_thin():
    assert resolve_evidence_tier(_raw(description=None)) == "thin"
    assert resolve_evidence_tier(_raw(description="  ")) == "thin"


def test_body_defaults_to_standard():
    assert resolve_evidence_tier(_raw()) == "standard"


def test_source_snapshot_at_iso():
    raw = _raw(raw={"source_snapshot_at": "2026-10-01T12:00:00Z"})
    ts = source_snapshot_at_from_raw(raw)
    assert ts == datetime(2026, 10, 1, 12, 0, tzinfo=timezone.utc)

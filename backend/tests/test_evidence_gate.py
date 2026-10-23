"""min_evidence parse + meta helpers."""

import pytest

from app.analytics.evidence_gate import (
    DEFAULT_MIN_EVIDENCE,
    evidence_meta,
    parse_min_evidence,
)


def test_default_is_standard():
    assert parse_min_evidence(None) == DEFAULT_MIN_EVIDENCE == "standard"


def test_all_disables_gate():
    assert parse_min_evidence("all") is None
    assert parse_min_evidence("") is None


def test_invalid_raises():
    with pytest.raises(ValueError):
        parse_min_evidence("gold")


def test_evidence_meta():
    assert evidence_meta(min_evidence="standard", excluded_thin_n=12) == {
        "min_evidence": "standard",
        "excluded_thin_n": 12,
    }
    assert evidence_meta(min_evidence=None, excluded_thin_n=0)["min_evidence"] == "all"

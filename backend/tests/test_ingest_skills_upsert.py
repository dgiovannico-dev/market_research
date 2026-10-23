"""Skills/rates sync: skip clear+reinsert when identity unchanged."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

from app.ingestion.job_skills import (
    desired_skill_identities,
    desired_skill_rows,
    rate_identity_from_classified,
    rate_identity_from_row,
    skill_identities,
    sync_job_rates,
    sync_job_skills,
)


class _TrackedList(list):
    """List that records clear() calls for write-amplification assertions."""

    def __init__(self, items=()):
        super().__init__(items)
        self.clear_calls = 0

    def clear(self):
        self.clear_calls += 1
        super().clear()


def _tech(tid: int, name: str) -> SimpleNamespace:
    return SimpleNamespace(id=tid, canonical_name=name)


def _skill(tid: int, importance: str = "mentioned", evidence_kind: str = "extracted"):
    return SimpleNamespace(
        technology_id=tid, importance=importance, evidence_kind=evidence_kind
    )


def _rate(
    *,
    amount_min=100.0,
    amount_max=120.0,
    currency="EUR",
    unit="day",
    rate_type="advertised",
):
    return SimpleNamespace(
        amount_min=amount_min,
        amount_max=amount_max,
        currency=currency,
        unit=unit,
        rate_type=rate_type,
    )


def test_skill_identities_are_set_of_triples():
    skills = [
        _skill(1, "mentioned"),
        _skill(2, "required", "inferred"),
        _skill(1, "mentioned"),  # duplicate collapses in frozenset
    ]
    assert skill_identities(skills) == frozenset(
        {(1, "mentioned", "extracted"), (2, "required", "inferred")}
    )


def test_desired_skill_rows_skips_unknown_tech():
    tech_map = {"Python": _tech(10, "Python")}
    classified = [
        {
            "canonical_name": "Python",
            "importance": "required",
            "extraction_method": "rules",
            "evidence_kind": "extracted",
            "confidence": 0.85,
            "evidence_span": "python",
        },
        {
            "canonical_name": "UnknownLang",
            "importance": "mentioned",
            "extraction_method": "rules",
            "evidence_kind": "extracted",
            "confidence": 0.5,
        },
    ]
    rows = desired_skill_rows(classified, tech_map)
    assert len(rows) == 1
    assert rows[0]["technology_id"] == 10
    assert desired_skill_identities(rows) == frozenset({(10, "required", "extracted")})


def test_sync_job_skills_noop_when_unchanged():
    db = MagicMock()
    existing = _TrackedList([_skill(10, "required")])
    job = SimpleNamespace(skills=existing)
    tech_map = {"Python": _tech(10, "Python")}
    classified = [
        {
            "canonical_name": "Python",
            "importance": "required",
            "extraction_method": "rules",
            "evidence_kind": "extracted",
            "confidence": 0.99,  # different confidence must not force rewrite
            "evidence_span": "other span",
        }
    ]

    wrote = sync_job_skills(db, job, classified_techs=classified, tech_map=tech_map)

    assert wrote is False
    assert existing.clear_calls == 0
    assert len(existing) == 1
    db.flush.assert_not_called()


def test_sync_job_skills_replaces_when_changed():
    db = MagicMock()
    existing = _TrackedList([_skill(10, "mentioned")])
    job = SimpleNamespace(skills=existing)
    tech_map = {
        "Python": _tech(10, "Python"),
        "Go": _tech(20, "Go"),
    }
    classified = [
        {
            "canonical_name": "Go",
            "importance": "required",
            "extraction_method": "rules",
            "evidence_kind": "extracted",
            "confidence": 0.8,
            "evidence_span": "go",
        }
    ]

    wrote = sync_job_skills(db, job, classified_techs=classified, tech_map=tech_map)

    assert wrote is True
    assert existing.clear_calls == 1
    db.flush.assert_called()
    assert len(existing) == 1
    assert existing[0].technology_id == 20
    assert existing[0].importance == "required"


def test_sync_job_skills_clears_when_new_empty():
    db = MagicMock()
    existing = _TrackedList([_skill(10)])
    job = SimpleNamespace(skills=existing)

    wrote = sync_job_skills(db, job, classified_techs=[], tech_map={})

    assert wrote is True
    assert existing.clear_calls == 1
    assert len(existing) == 0


def test_rate_identity_helpers():
    row = _rate(amount_min=50.0, amount_max=None, currency="USD", unit="hour")
    classified = {
        "amount_min": 50.0,
        "amount_max": None,
        "currency": "USD",
        "unit": "hour",
    }
    assert rate_identity_from_row(row) == rate_identity_from_classified(classified)


def test_sync_job_rates_noop_when_single_advertised_unchanged():
    db = MagicMock()
    existing = _TrackedList([_rate()])
    job = SimpleNamespace(rates=existing)
    classified = {
        "amount_min": 100.0,
        "amount_max": 120.0,
        "currency": "EUR",
        "unit": "day",
        "evidence_text": "changed evidence must not force rewrite",
        "confidence": 0.1,
    }

    wrote = sync_job_rates(db, job, classified_rate=classified)

    assert wrote is False
    assert existing.clear_calls == 0
    assert len(existing) == 1
    db.flush.assert_not_called()


def test_sync_job_rates_replaces_when_amount_changes():
    db = MagicMock()
    existing = _TrackedList([_rate(amount_min=100.0)])
    job = SimpleNamespace(rates=existing)
    classified = {
        "amount_min": 200.0,
        "amount_max": 120.0,
        "currency": "EUR",
        "unit": "day",
        "rate_type": "advertised",
        "extraction_method": "rules",
        "evidence_kind": "extracted",
        "confidence": 0.7,
    }

    wrote = sync_job_rates(db, job, classified_rate=classified)

    assert wrote is True
    assert existing.clear_calls == 1
    db.flush.assert_called()
    assert len(existing) == 1
    assert existing[0].amount_min == 200.0


def test_sync_job_rates_noop_when_both_empty():
    db = MagicMock()
    existing = _TrackedList()
    job = SimpleNamespace(rates=existing)

    wrote = sync_job_rates(db, job, classified_rate=None)

    assert wrote is False
    assert existing.clear_calls == 0
    db.flush.assert_not_called()


def test_sync_job_rates_clears_when_rate_removed():
    db = MagicMock()
    existing = _TrackedList([_rate()])
    job = SimpleNamespace(rates=existing)

    wrote = sync_job_rates(db, job, classified_rate=None)

    assert wrote is True
    assert existing.clear_calls == 1
    assert len(existing) == 0

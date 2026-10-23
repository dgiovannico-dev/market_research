"""Wave 3b/4: domain soft-expire policy + classification facade purity."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.domain.classification import ClassificationResult, classify_job
from app.domain.job.soft_expire_policy import SoftExpirePlan, plan_soft_expire


def test_plan_soft_expire_gates_unseen_on_dump_complete():
    now = datetime(2026, 10, 23, 12, 0, tzinfo=timezone.utc)
    seen = now - timedelta(hours=1)
    incomplete = plan_soft_expire(
        seen_before=seen, dump_complete=False, now=now, stale_after_days=45
    )
    assert isinstance(incomplete, SoftExpirePlan)
    assert incomplete.run_unseen_expire is False
    assert incomplete.age_cutoff == now - timedelta(days=45)

    complete = plan_soft_expire(
        seen_before=seen, dump_complete=True, now=now, stale_after_days=45
    )
    assert complete.run_unseen_expire is True
    assert complete.seen_before == seen


def test_domain_classify_job_works():
    result = classify_job(
        title="Senior Python Freelancer remote Milan",
        description="Looking for a senior freelance Python engineer, fully remote, Italy.",
        location="Milan, Italy",
    )
    assert isinstance(result, ClassificationResult)
    assert result.contract_type in {"freelance", "b2b", "employment", "temporary", "unknown"}


def test_domain_classification_package_has_no_sqlalchemy():
    root = Path(__file__).resolve().parents[1] / "app" / "domain" / "classification"
    text = (root / "__init__.py").read_text(encoding="utf-8")
    assert "sqlalchemy" not in text.lower()
    # Underlying rules module must stay Session-free (Wave 4 gate).
    rules = Path(__file__).resolve().parents[1] / "app" / "classification" / "rules.py"
    assert "sqlalchemy" not in rules.read_text(encoding="utf-8").lower()
    assert "Session" not in rules.read_text(encoding="utf-8")

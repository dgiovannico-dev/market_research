"""Study Advisor: thin corpus never invents stack."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.analytics.study_advice import (
    StudyMilestone,
    StudyPlan,
    build_evidence_pack,
    coerce_llm_plan_payload,
    compact_evidence_for_llm,
    stub_study_plan,
    validate_plan_against_evidence,
)
from app.storage.db import Base, get_db


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def api_client(db_session):
    from app.main import app

    def _override():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_thin_evidence_stub_no_invented_stack(db_session):
    evidence = build_evidence_pack(
        db_session,
        skills=["Java"],  # <3 skills → thin
        hours_per_week=5,
        modality="employed_part_time",
        horizon_weeks=6,
    )
    assert evidence["coverage"]["thin"] is True
    plan = stub_study_plan(evidence)
    allowed = {c["technology"] for c in evidence["candidates"] if c.get("technology")}
    for tech in plan.stack_target:
        assert tech in allowed


def test_validate_drops_ungrounded_skills():
    evidence = {
        "skills": ["Java", "Spring", "Kotlin"],
        "candidates": [{"technology": "Kubernetes"}, {"technology": "Terraform"}],
        "limits": [],
        "coverage": {"thin": False},
        "modality": "intensive",
        "hours_per_week": 20,
        "horizon_weeks": 4,
    }
    plan = StudyPlan(
        title="x",
        horizon_weeks=4,
        modality="intensive",
        hours_per_week=20,
        stack_target=["Kubernetes", "InventedCloud", "Java"],
        milestones=[
            StudyMilestone(
                week=1,
                title="K8s",
                skills=["Kubernetes", "FakeTech"],
                evidence_refs=["candidate:Kubernetes"],
            )
        ],
        weekly_template=[],
        limits=[],
        source="llm",
    )
    cleaned = validate_plan_against_evidence(plan, evidence)
    assert "InventedCloud" not in cleaned.stack_target
    assert "Kubernetes" in cleaned.stack_target
    assert "Java" in cleaned.stack_target
    assert all(s != "FakeTech" for m in cleaned.milestones for s in m.skills)


def test_coerce_llm_plan_payload_fixes_string_stack():
    evidence = {
        "skills": ["Java", "Spring Boot", "AWS"],
        "candidates": [{"technology": "Kubernetes"}, {"technology": "Azure"}],
        "modality": "employed_part_time",
        "hours_per_week": 6,
        "horizon_weeks": 8,
    }
    raw = {
        "title": "Plan",
        "stack_target": "Kubernetes and Azure",
        "milestones": [
            {"skill": "Kubernetes", "title": "Learn K8s"},
            {"week": "4", "skills": "Azure", "title": "Cloud"},
        ],
        "limits": "be careful",
    }
    coerced = coerce_llm_plan_payload(raw, evidence=evidence)
    plan = StudyPlan.model_validate({**coerced, "source": "llm"})
    assert plan.stack_target == ["Kubernetes", "Azure"]
    assert plan.milestones[0].week >= 1
    assert "Kubernetes" in plan.milestones[0].skills
    assert plan.limits == ["be careful"]


def test_compact_evidence_for_llm_fits_small_context():
    evidence = {
        "modality": "employed_part_time",
        "hours_per_week": 6,
        "horizon_weeks": 8,
        "skills": ["Java", "Spring Boot", "AWS"],
        "certifications": [],
        "coverage": {"thin": False, "candidate_count": 12},
        "candidates": [
            {
                "technology": f"Tech{i}",
                "anchor_skill": "AWS",
                "support": 100 + i,
                "lift": 2.0,
                "gap_priority": 50.0,
                "score": 0.9,
                "irreplaceability_score": 0.7,
                "growth_pct": 10.0,
                "drilldown": {"relations_href": "/relations?seed=x" * 40},
                "limits": ["long limit text " * 20],
                "rate_check": {
                    "sample_size": 10,
                    "rate": {"median": 500.0, "p25": 100.0, "p75": 900.0},
                    "limits": "Advertised amounts...",
                },
            }
            for i in range(12)
        ],
        "related_certifications": [
            {
                "slug": f"cert{i}",
                "display_name": f"Cert {i}",
                "mentions": i,
                "drilldown": {"certifications_href": "/certifications"},
                "limits": "Observed certification mentions...",
            }
            for i in range(10)
        ],
        "limits": ["a", "b", "c"] * 5,
        "disclaimer": "Observed corpus only",
    }
    raw_full = __import__("json").dumps(evidence)
    compact = compact_evidence_for_llm(evidence)
    assert len(compact) < len(raw_full)
    assert len(compact) <= 4500
    parsed = __import__("json").loads(compact)
    assert "Tech0" in {c["technology"] for c in parsed["candidates"]}
    assert "drilldown" not in parsed["candidates"][0]


def test_study_advice_plan_endpoint_thin(api_client):
    res = api_client.post(
        "/api/v1/profile/study-advice/plan",
        json={
            "skills": ["A"],
            "hours_per_week": 4,
            "modality": "employed_part_time",
            "horizon_weeks": 4,
        },
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["mode"] == "stub"
    assert body["plan"]["source"] == "stub"
    for tech in body["plan"]["stack_target"]:
        assert tech in {c["technology"] for c in body["evidence"]["candidates"]}

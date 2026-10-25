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

"""Certifications taxonomy extract + top KPI shape."""

from app.analytics.certifications import top_certifications
from app.classification.certs import extract_certifications, load_cert_taxonomy
from app.storage.db import SessionLocal


def test_cert_taxonomy_loads():
    rows = load_cert_taxonomy()
    assert isinstance(rows, list)
    assert len(rows) >= 100
    slugs = [r.get("slug") for r in rows]
    assert len(slugs) == len(set(slugs))
    assert all(r.get("slug") and r.get("display_name") for r in rows)


def test_extract_ckad_and_aws_saa():
    title = "Senior Platform Engineer — CKAD preferred"
    description = (
        "We require AWS Certified Solutions Architect (SAA-C03) and experience with K8s. "
        "Terraform Associate is a plus."
    )
    found = extract_certifications(title, description)
    slugs = {item["slug"] for item in found}
    assert "ckad" in slugs
    assert "aws-saa" in slugs
    assert "terraform-associate" in slugs
    ckad = next(i for i in found if i["slug"] == "ckad")
    assert ckad["extraction_method"] == "rules"
    assert ckad["evidence_span"]


def test_top_certifications_shape():
    db = SessionLocal()
    try:
        try:
            out = top_certifications(db, days=90, lens="market", top_n=10)
        except Exception as exc:  # noqa: BLE001 — empty/offline DB in unit CI
            import pytest

            pytest.skip(f"DB unavailable for top_certifications: {exc}")
        assert out.get("lens") == "market"
        assert isinstance(out.get("items"), list)
        assert "period_days" in out
        for row in out.get("items") or []:
            assert "certification" in row
            assert "job_mentions" in row
            assert row["job_mentions"] >= 1
    finally:
        db.rollback()
        db.close()

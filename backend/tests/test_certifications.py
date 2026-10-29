"""Certifications taxonomy extract + top KPI shape."""

from collections import Counter

from app.analytics.certifications import top_certifications
from app.classification.certs import (
    _compiled,
    extract_certifications,
    load_cert_taxonomy,
)
from app.storage.db import SessionLocal


def test_cert_taxonomy_loads():
    load_cert_taxonomy.cache_clear()
    _compiled.cache_clear()
    rows = load_cert_taxonomy()
    assert isinstance(rows, list)
    assert len(rows) >= 100
    slugs = [r.get("slug") for r in rows]
    assert len(slugs) == len(set(slugs))
    assert all(r.get("slug") and r.get("display_name") for r in rows)
    names = [str(r.get("display_name") or "").strip().lower() for r in rows]
    dup_names = [n for n, c in Counter(names).items() if c > 1]
    assert not dup_names, f"duplicate display_name in taxonomy: {dup_names}"
    alias_owners: dict[str, str] = {}
    for r in rows:
        slug = str(r.get("slug") or "")
        for raw in [r.get("display_name"), *(r.get("aliases") or [])]:
            key = str(raw or "").strip().lower()
            if not key:
                continue
            prev = alias_owners.get(key)
            assert prev in (None, slug), f"alias {key!r} owned by {prev} and {slug}"
            alias_owners[key] = slug


def test_extract_csm_once():
    load_cert_taxonomy.cache_clear()
    _compiled.cache_clear()
    found = extract_certifications(
        "Scrum coach",
        "CSM or Certified Scrum Master required. Scrum Alliance CSM preferred.",
    )
    slugs = [i["slug"] for i in found]
    assert slugs.count("csm") == 1
    assert "scrum-csm" not in slugs
    names = [i["display_name"].lower() for i in found]
    assert names.count("certified scrummaster") == 1


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

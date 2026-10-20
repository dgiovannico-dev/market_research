from app.classification.rules import classify_job


def test_classify_freelance_remote_java():
    result = classify_job(
        title="Senior Java Contractor",
        description="Looking for a freelance Java Spring Boot engineer. Fully remote. B2B.",
        location="Europe",
        salary_text="€600/day",
        tags=["java", "spring"],
    )
    assert result.contract_type in {"freelance", "b2b"}
    assert result.remote_type == "remote"
    assert result.seniority == "senior"
    names = {t["canonical_name"] for t in result.technologies}
    assert "Java" in names
    assert result.rate is not None
    assert result.rate["amount_min"] == 600
    assert result.rate["unit"] == "day"


def test_unknown_contract_when_ambiguous():
    result = classify_job(
        title="Software Engineer",
        description="Join our team building APIs.",
        location="Berlin",
    )
    assert result.contract_type == "unknown"
    assert result.country_code == "DE"

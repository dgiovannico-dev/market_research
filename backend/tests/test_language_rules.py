"""Unit tests for human-language requirement extraction."""

from app.classification.language_rules import extract_language_requirements
from app.classification.rules import classify_job


def test_english_and_italian_required():
    langs = extract_language_requirements(
        title="Senior Engineer",
        description="Fluent English and Italian required. CEFR C1 preferred.",
    )
    assert langs == ["en", "it"]


def test_java_developer_alone_is_not_a_language():
    langs = extract_language_requirements(
        title="Java developer",
        description="Build microservices with Java and Spring Boot.",
    )
    assert langs == []


def test_deutsch_and_francais():
    langs = extract_language_requirements(
        description="Deutschkenntnisse und Français exigés pour le poste.",
    )
    assert "de" in langs
    assert "fr" in langs


def test_classify_job_sets_language_requirements():
    result = classify_job(
        title="Backend",
        description="Must speak English. Remote Italy.",
    )
    assert "en" in result.language_requirements

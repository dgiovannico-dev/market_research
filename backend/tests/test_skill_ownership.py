"""Profile skill matching: aliases / case must resolve to taxonomy names."""

from __future__ import annotations

from app.analytics.skill_ownership import names_match_owned, resolve_owned_skill_names


def test_resolve_owned_skill_names_case_and_alias():
    owned = resolve_owned_skill_names(["java", "SPRING BOOT", "aws", "  "])
    assert owned == {"Java", "Spring Boot", "AWS"}


def test_names_match_owned_case_insensitive():
    owned = {"Java", "AWS"}
    assert names_match_owned("java", owned)
    assert names_match_owned("Java", owned)
    assert not names_match_owned("Python", owned)

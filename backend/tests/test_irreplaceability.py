"""Unit tests for Stack Compass irreplaceability scoring."""

from app.analytics.irreplaceability import (
    STACK_COMPASS_SCORE_VERSION,
    irreplaceability_score,
    normalize_min_max,
    score_components_for_candidate,
)


def test_normalize_min_max():
    assert normalize_min_max(0, 0, 10) == 0.0
    assert normalize_min_max(10, 0, 10) == 1.0
    assert normalize_min_max(5, 0, 10) == 0.5
    assert normalize_min_max(1, 1, 1) == 0.0


def test_irreplaceability_score_penalizes_generic():
    scarce = irreplaceability_score(
        complement=0.8, rarity=0.9, demand=0.7, generic_penalty=0.1
    )
    commodity = irreplaceability_score(
        complement=0.2, rarity=0.1, demand=0.9, generic_penalty=0.9
    )
    assert scarce > commodity
    assert scarce <= 1.0


def test_score_components_version_and_keys():
    comps = score_components_for_candidate(
        lift=2.5,
        support=10,
        max_support=20,
        marginal_freq=5,
        max_marginal=100,
        demand_score=8.0,
        max_demand=10.0,
    )
    assert comps["score_version"] == STACK_COMPASS_SCORE_VERSION
    assert "complement" in comps
    assert "rarity_proxy" in comps
    assert "demand_norm" in comps
    assert "generic_penalty" in comps
    assert "irreplaceability_score" in comps
    # High lift → higher complement; low marginal → higher rarity
    assert comps["complement"] > 0.3
    assert comps["rarity_proxy"] > 0.8

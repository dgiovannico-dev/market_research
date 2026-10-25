"""Irreplaceability / stack-complement score helpers (SPEC-stack-compass)."""

from __future__ import annotations

from typing import Any

STACK_COMPASS_SCORE_VERSION = 1


def _clamp01(x: float) -> float:
    if x != x:  # NaN
        return 0.0
    return max(0.0, min(1.0, float(x)))


def normalize_min_max(value: float, lo: float, hi: float) -> float:
    if hi <= lo:
        return 0.0
    return _clamp01((value - lo) / (hi - lo))


def irreplaceability_score(
    *,
    complement: float,
    rarity: float,
    demand: float,
    generic_penalty: float,
) -> float:
    """Weighted score in roughly [-0.2, 1.0]; callers may clamp display."""
    return round(
        0.45 * _clamp01(complement)
        + 0.25 * _clamp01(rarity)
        + 0.30 * _clamp01(demand)
        - 0.20 * _clamp01(generic_penalty),
        4,
    )


def score_components_for_candidate(
    *,
    lift: float | None,
    support: int,
    max_support: int,
    marginal_freq: int,
    max_marginal: int,
    demand_score: float,
    max_demand: float,
) -> dict[str, Any]:
    """Derive normalized components from co-occurrence + gap demand."""
    lift_v = float(lift) if lift is not None and lift == lift else 0.0
    # Lift often ~0.5–5; soft-cap at 5 for norm.
    complement = _clamp01(lift_v / 5.0) if lift_v > 0 else _clamp01(support / max(max_support, 1))
    # Rarity: low marginal frequency → high rarity.
    rarity = 1.0 - normalize_min_max(float(marginal_freq), 0.0, float(max(max_marginal, 1)))
    demand = normalize_min_max(demand_score, 0.0, max(max_demand, 1e-9))
    # Generic: high freq + low lift.
    generic_penalty = _clamp01(
        normalize_min_max(float(marginal_freq), 0.0, float(max(max_marginal, 1)))
        * (1.0 - complement)
    )
    score = irreplaceability_score(
        complement=complement,
        rarity=rarity,
        demand=demand,
        generic_penalty=generic_penalty,
    )
    return {
        "complement": round(complement, 4),
        "rarity_proxy": round(rarity, 4),
        "demand_norm": round(demand, 4),
        "generic_penalty": round(generic_penalty, 4),
        "irreplaceability_score": score,
        "score_version": STACK_COMPASS_SCORE_VERSION,
    }

"""Semantic metric catalog for MCP (aligned with analytics KPIs)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

EvidenceKind = Literal[
    "observed",
    "extracted",
    "inferred",
    "derived",
    "estimated",
    "manually_verified",
]


class MetricDef(BaseModel):
    key: str
    name: str
    definition: str
    evidence_kind: EvidenceKind = "derived"
    unit: str | None = None
    allowed_filters: list[str] = Field(default_factory=list)
    preferred_endpoint: str | None = None
    notes: str | None = None


_FILTERS = ["period_days", "technologies", "countries", "source_keys", "contract_types"]

_METRICS: list[MetricDef] = [
    MetricDef(
        key="unique_jobs_observed",
        name="Unique jobs observed",
        definition="Canonical (deduplicated) jobs with published_at in period.",
        evidence_kind="observed",
        allowed_filters=_FILTERS,
        preferred_endpoint="GET /api/v1/dashboard/summary",
    ),
    MetricDef(
        key="freelance_b2b_verified",
        name="Freelance/B2B verified",
        definition="Jobs classified freelance/b2b/contractor with confidence >= 0.7.",
        evidence_kind="inferred",
        allowed_filters=_FILTERS,
        preferred_endpoint="GET /api/v1/dashboard/summary",
    ),
    MetricDef(
        key="observed_demand_growth_pct",
        name="Observed demand growth %",
        definition="Percent change vs previous equal-length window of observed unique jobs.",
        evidence_kind="derived",
        unit="percent",
        allowed_filters=["period_days", "technologies", "countries"],
        preferred_endpoint="GET /api/v1/dashboard/summary",
        notes="Not total market growth; mark insufficient_data when sample is low.",
    ),
    MetricDef(
        key="jobs_with_published_rate",
        name="Jobs with published rate",
        definition="Jobs with at least one extracted/advertised rate record.",
        evidence_kind="observed",
        allowed_filters=_FILTERS,
        preferred_endpoint="GET /api/v1/dashboard/summary",
        notes="NULL rates are never treated as zero.",
    ),
    MetricDef(
        key="remote_jobs_observed",
        name="Remote jobs observed",
        definition="Jobs classified remote_type=remote.",
        evidence_kind="inferred",
        allowed_filters=_FILTERS,
        preferred_endpoint="GET /api/v1/dashboard/summary",
    ),
    MetricDef(
        key="rates_distribution",
        name="Rates distribution",
        definition="Median/percentiles of non-NULL advertised rates in period.",
        evidence_kind="extracted",
        unit="currency",
        allowed_filters=_FILTERS,
        preferred_endpoint="GET /api/v1/market/rates",
        notes=(
            "Refuse invented medians when sample_size is 0. "
            "Default min_evidence=standard excludes thin tier jobs."
        ),
    ),
    MetricDef(
        key="countries_breakdown",
        name="Countries breakdown",
        definition="Observed job counts by country_code.",
        evidence_kind="observed",
        allowed_filters=["period_days", "technologies", "source_keys"],
        preferred_endpoint="GET /api/v1/market/countries",
    ),
    MetricDef(
        key="skill_cooccurrence",
        name="Skill co-occurrence",
        definition="Pairwise skill support/lift/jaccard on observed jobs.",
        evidence_kind="derived",
        allowed_filters=["period_days", "technologies", "countries"],
        preferred_endpoint="GET /api/v1/market/skills/cooccurrence",
        notes=(
            "Not causal; guided mode must disclaimer. "
            "Default min_evidence=standard excludes thin tier jobs."
        ),
    ),
    MetricDef(
        key="technology_trends",
        name="Technology trends",
        definition="Half-period comparison of technology mentions; insufficient_data when low support.",
        evidence_kind="derived",
        allowed_filters=["period_days", "technologies", "countries"],
        preferred_endpoint="GET /api/v1/market/trends",
        notes="Default min_evidence=standard excludes thin tier from mention counts.",
    ),
    MetricDef(
        key="data_quality",
        name="Data quality / coverage",
        definition="Missing rates, source mix, and coverage metrics for this database.",
        evidence_kind="derived",
        allowed_filters=["period_days"],
        preferred_endpoint="GET /api/v1/market/quality",
        notes=(
            "Full active corpus incl. thin tier (no min_evidence gate); "
            "metrics.pct_thin and by_source.pct_thin for operator thin share."
        ),
    ),
    MetricDef(
        key="sources_active_coverage",
        name="ACTIVE source coverage",
        definition="Runnable/ACTIVE sources and their contribution to observed jobs.",
        evidence_kind="observed",
        allowed_filters=["period_days", "source_keys"],
        preferred_endpoint="GET /api/v1/sources",
    ),
]


def get_semantic_catalog() -> list[MetricDef]:
    return list(_METRICS)


def metric_keys() -> set[str]:
    return {m.key for m in _METRICS}


def get_metric(key: str) -> MetricDef | None:
    for m in _METRICS:
        if m.key == key:
            return m
    return None

# Spec: analytics

## Objective

Compute market KPIs and slices from stored jobs only: summary, rates, countries, skill co-occurrence, trends, and data quality—each with sample size, period, coverage, and limits. Never infer market saturation from volume alone.

## In scope

### Core (shipped / in progress)

- Dashboard summary KPIs (period window).
- Rates distribution (exclude NULL; never coerce to zero).
- Countries / geography breakdown.
- Skill co-occurrence (support, lift, jaccard) with causation disclaimer in guided copy.
- Technology trends (half-period comparison, `insufficient_data` when support is low).
- Quality / coverage metrics (missing rates, source mix, errors/duplicates where exposed).

### Required analytic outcomes (product target)

Each KPI must expose or document: **sample**, **period**, **coverage**, **definition**.

| Outcome | Notes |
|---------|--------|
| Observed & unique job counts | Dedup-aware |
| New jobs per period | Sync/first-seen |
| Monthly / annual trends | Observed series only |
| Demand by skill & tech combinations | Co-occurrence + filters |
| Demand by country & sector | When fields present |
| Contract type distribution | When classified |
| Remote / hybrid / on-site | When classified |
| Median & percentile rates | NULL excluded; separate pay kinds |
| Share of jobs with declared pay | Quality metric |
| Seniority / experience | When extracted |
| Assignment duration | When present |
| **Human language requirements** | `Job.language_requirements` aggregates — see [SPEC-dashboard-charts.md](SPEC-dashboard-charts.md) |
| Java + AI/RAG demand | Filtered observed counts |
| Python + LLM demand | Filtered observed counts |
| Cloud / AI eval / AI security demand | Filtered observed counts |
| Source geo/temporal coverage | Catalog + quality |
| Extraction errors & duplicates | Ops/quality |

**Chart cockpit:** full KPI↔viz mapping lives in [SPEC-dashboard-charts.md](SPEC-dashboard-charts.md) (Draft 2026-10-22).

## Out of scope

- Forecasting total market size or saturation from volume alone.
- Causal claims from co-occurrence.
- Mixing incomparable national statistics into job KPIs (stats-ingest Later).
- Presenting procurement totals as day rates.

## Acceptance criteria

- [x] `GET /api/v1/dashboard/summary` returns KPIs with `definition`, `sample_size`, `limits`, `evidence_kind`.
- [x] Rates endpoints omit fabricated zeros for missing amounts.
- [x] Trends mark insufficient data instead of inventing growth.
- [x] Co-occurrence respects `min_support` and returns `jobs_analyzed`.
- [x] Unit tests cover analytics helpers; API smoke covers routes.
- [ ] Explicit combo filters (Java+AI/RAG, Python+LLM) documented in UI/API when productized (Next/Later as needed).

## Key paths

- `backend/app/analytics/`
- `backend/app/api/v1/router.py`
- `backend/app/api/v1/market_extra.py`
- ADR: [../decisions/ADR-001-evidence-first-kpis.md](../decisions/ADR-001-evidence-first-kpis.md)
- Coverage: [../sources/COVERAGE_GAPS.md](../sources/COVERAGE_GAPS.md)

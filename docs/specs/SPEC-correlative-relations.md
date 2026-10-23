# Spec: Correlative Relations + Temporal Series

**Status:** Accepted (2026-10-22) — waves 0–5 implemented  
**Extends:** [SPEC-dashboard-charts.md](SPEC-dashboard-charts.md), [SPEC-analytics.md](SPEC-analytics.md)  
**Policy:** ADR-001 (observed ≠ market size); no causal claims from co-occurrence.

## Intent

Decision cockpit that relates **technologies × countries × time** (and reuses skill×skill co-occurrence) under one sticky **period**, **lens**, and **country** filter.

## Scope (v1 waves 0–2) — done

1. **PeriodChip** — sticky chips `7|14|30|90|180|365` writing `prefs.period_days` (same global period everywhere).
2. **Page `/relations`** — Relations dashboard:
   - Tech×tech heat (from existing co-occurrence, top-N by lift/support)
   - Tech×country matrix (counts / share)
   - Temporal series: top technologies by week; top countries by week
3. **APIs**
   - `GET /api/v1/market/matrix/tech-country`
   - `GET /api/v1/market/series/technologies`
   - `GET /api/v1/market/series/countries`
4. Nav entry under Explore zone; i18n en/it.

## Scope (wave 3) — done

1. **Language × country matrix** — `GET /api/v1/market/matrix/language-country` (same cell shape as tech×country; human languages only).
2. **Rate median series** — `GET /api/v1/market/series/rates` — median advertised `amount_min` over time keyed by `CURRENCY/unit`; grain auto like other series.
3. Relations UI sections for both; reuse HeatMatrix + MultiSeriesChart; en/it copy.

## Scope (wave 4) — done

1. **Role family × technology matrix** — `GET /api/v1/market/matrix/role-tech` using `Job.role_family` × skills (`JobSkill`/`Technology`). Skip null/empty role_family.
2. Relations UI heat section; en/it copy; reuse HeatMatrix.
3. Unit tests for aggregation + empty corpus.

## Scope (wave 5) — done

1. **Seniority × technology matrix** — `GET /api/v1/market/matrix/seniority-tech` using `Job.seniority` × skills (`JobSkill`/`Technology`). Skip null/empty seniority.
2. Relations UI heat section; en/it copy; reuse HeatMatrix.
3. Unit tests for aggregation + empty corpus + min_cell.

## Out of scope (later)

Combo filters, independent per-chart periods.

## Contracts

### PeriodChip
- Options: `[7, 14, 30, 90, 180, 365]`
- Calls `setPeriodDays` from `DashboardPrefsProvider`
- Visible on Executive header + Relations header (and reusable elsewhere)

### `GET /market/matrix/tech-country`
Query: `days`, `lens`, `query_ids`, `country_code`, `min_evidence`, `top_tech` (default 12), `top_country` (default 10), `min_cell` (default 2).  
Response:
```json
{
  "period_days": 30,
  "sample_size": 1527,
  "technologies": ["Java", "..."],
  "countries": ["CH", "DE", "..."],
  "cells": [{"technology": "Java", "country_code": "CH", "jobs": 42}],
  "excluded_thin_n": 0,
  "limits": "Observed inventory only; cells below min_cell omitted."
}
```

### `GET /market/matrix/seniority-tech`
Query: `days`, `lens`, `query_ids`, `country_code`, `min_evidence`, `top_seniority` (default 8), `top_tech` (default 12), `min_cell` (default 2).  
Response:
```json
{
  "period_days": 30,
  "sample_size": 1527,
  "seniorities": ["senior", "mid", "..."],
  "technologies": ["Java", "..."],
  "cells": [{"seniority": "senior", "technology": "Java", "jobs": 42}],
  "excluded_thin_n": 0,
  "limits": "Observed inventory only; cells below min_cell omitted. Jobs without seniority excluded from axes."
}
```

### `GET /market/series/technologies` | `/countries`
Query: `days`, `lens`, `query_ids`, `country_code`, `min_evidence`, `top` (default 8), `grain` optional (`day|week|month`; auto from days if omitted).  
Response:
```json
{
  "period_days": 90,
  "grain": "week",
  "sample_size": 2000,
  "series": [
    {"key": "Java", "points": [{"bucket": "2026-W12", "count": 10}, ...]}
  ],
  "limits": "..."
}
```

### Charts
- Reuse `ChartFrame` (period footer, `n=`, top-N, table toggle).
- Heat: ECharts heatmap; Series: multi-line.
- Thin/empty states when `sample_size` low or no cells.

## Acceptance

- [x] Changing PeriodChip updates Relations + Executive fetches
- [x] Matrix and series return lens/country-aware corpora
- [x] Unit tests for matrix aggregation + series bucketing
- [x] `/relations` in nav; en+it copy
- [x] Language×country matrix + rates series APIs and Relations sections (wave 3)
- [x] Role×tech matrix API and Relations section (wave 4)
- [x] Seniority×tech matrix API and Relations section (wave 5)

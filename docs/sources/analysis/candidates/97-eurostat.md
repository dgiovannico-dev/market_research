# Eurostat (catalog_id=97)

| Field | Value |
|-------|-------|
| Analysis | DOCUMENTED |
| Role | `reference_not_jobs` — category **E**; not `RawJob` ingest |
| verification_status | VALIDATED |
| access_mode | public_api |
| connector_key | — |

In-repo: `backend/app/stats/eurostat.py`; FMI `GET /api/v1/stats/eurostat/series`.

## Official / docs
- Official: https://ec.europa.eu/eurostat/
- Docs: https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/
- Catalog note: Official statistics reference only — never mixed into observed job KPIs.

## Access path (reference import)
- Preferred: JSON-stat dissemination API (allowlisted datasets in code).
- `GET …/statistics/1.0/data/{dataset}?format=JSON&geo=&time=`
- FMI proxy: `GET /api/v1/stats/eurostat/series?dataset=&geo=&time=`
- Auth: None
- Series / tables: `earn_ses_hourly`, `earn_ses18_hourly`, `une_rt_a`

## FMI use (context KPIs — not RawJob)
- EU unemployment + earnings context bands; `evidence_kind=official_statistics_reference`.
- Store: `provider`, `series_id`, `geo`, `time`, `value`, `vintage`, `evidence_kind`.
- Never merge into observed job KPI numerators without explicit labeling (ADR-001).

## Field map → reference facts (not RawJob)
| Source | FMI field | Notes |
|--------|-----------|-------|
| JSON-stat cube value | `reference_metric` | Official stats slice |
| Dataset + filters | `series_id` | Allowlisted only |

## Geo / compliance
- EU / EFTA geo codes; multi-country dashboards.
- Authorized API only (ADR-003).

## Gaps / next step
- Expand allowlist deliberately; document NACE/ISCO dimensions before UI exposure.

# UK National Careers Service (catalog_id=123)

| Field | Value |
|-------|-------|
| Analysis | DOCUMENTED |
| Role | `reference_not_jobs` — category **E**; not `RawJob` ingest |
| verification_status | UNDER_REVIEW |
| access_mode | portal |
| connector_key | — |

## Official / docs
- Official: https://nationalcareers.service.gov.uk/
- Docs: https://nationalcareers.service.gov.uk/
- Catalog note: Official statistics — import via datasets/API; do not mix incomparable series. Not wired as job connector.

## Access path (reference import)
- Preferred: National Careers Service (LMI for All API for developers).
- LMI for All API (skills/occupation data) where licensed.
- Auth: per provider (portal).
- Series / tables: Occupation profiles, forecasts, UK SOC-aligned summaries.

## FMI use (context KPIs — not RawJob)
- UK career/occupation context in briefs (not job crawl).
- Store: `provider`, `series_id`, `geo`, `time`, `value`, `vintage`, `evidence_kind`.
- Never merge into observed job KPI numerators without explicit labeling (ADR-001).

## Field map → reference facts (not RawJob)
| Source | FMI field | Notes |
|--------|-----------|-------|
| Agency series / survey row | `reference_metric` | Numeric or categorical benchmark |
| Publication date | `vintage` | Survey year or release date |
| Geography | `geo` | ISO3166 / agency code |

## Geo / compliance
- UK.
- Lawful download/API only; no paywall or ToS-prohibited scraping (ADR-003).

## Gaps / next step
- Register for LMI for All; respect attribution.

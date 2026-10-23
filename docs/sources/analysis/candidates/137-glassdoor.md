# Glassdoor (catalog_id=137)

| Field | Value |
|-------|-------|
| Analysis | DOCUMENTED |
| Role | `survey_salary_reference` — category **F**; not `RawJob` ingest |
| verification_status | UNDER_REVIEW |
| access_mode | report_or_dataset |
| connector_key | — |

## Official / docs
- Official: https://www.glassdoor.com/
- Docs: https://www.glassdoor.com/
- Catalog note: Survey/report — use lawful download/import; do not scrape paywalled pages. Not a live job connector.

## Access path (reference import)
- Preferred: Glassdoor salary estimates (web); separate from Glassdoor Jobs (category A).
- Partner/publisher APIs only; no HTML scrape.
- Auth: per provider (report_or_dataset).
- Series / tables: Employer salary self-reports and estimates.

## FMI use (context KPIs — not RawJob)
- Comp context if licensed feed; else manual import snapshots.
- Store: `provider`, `series_id`, `geo`, `time`, `value`, `vintage`, `evidence_kind`.
- Never merge into observed job KPI numerators without explicit labeling (ADR-001).

## Field map → reference facts (not RawJob)
| Source | FMI field | Notes |
|--------|-----------|-------|
| Agency series / survey row | `reference_metric` | Numeric or categorical benchmark |
| Publication date | `vintage` | Survey year or release date |
| Geography | `geo` | ISO3166 / agency code |

## Geo / compliance
- Multi-country (coverage varies).
- Lawful download/API only; no paywall or ToS-prohibited scraping (ADR-003).

## Gaps / next step
- Legal/partner path required for automation.

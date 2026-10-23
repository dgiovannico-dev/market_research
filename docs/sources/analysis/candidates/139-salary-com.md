# Salary.com (catalog_id=139)

| Field | Value |
|-------|-------|
| Analysis | DOCUMENTED |
| Role | `survey_salary_reference` — category **F**; not `RawJob` ingest |
| verification_status | UNDER_REVIEW |
| access_mode | report_or_dataset |
| connector_key | — |

## Official / docs
- Official: https://www.salary.com/
- Docs: https://www.salary.com/
- Catalog note: Survey/report — use lawful download/import; do not scrape paywalled pages. Not a live job connector.

## Access path (reference import)
- Preferred: Salary.com HR compensation data (commercial).
- Product APIs via commercial agreement.
- Auth: per provider (report_or_dataset).
- Series / tables: Salary ranges by job family and geography.

## FMI use (context KPIs — not RawJob)
- Manual or licensed import for benchmark bands.
- Store: `provider`, `series_id`, `geo`, `time`, `value`, `vintage`, `evidence_kind`.
- Never merge into observed job KPI numerators without explicit labeling (ADR-001).

## Field map → reference facts (not RawJob)
| Source | FMI field | Notes |
|--------|-----------|-------|
| Agency series / survey row | `reference_metric` | Numeric or categorical benchmark |
| Publication date | `vintage` | Survey year or release date |
| Geography | `geo` | ISO3166 / agency code |

## Geo / compliance
- US-focused.
- Lawful download/API only; no paywall or ToS-prohibited scraping (ADR-003).

## Gaps / next step
- No public API path documented.

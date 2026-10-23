# Statistics Netherlands (catalog_id=124)

| Field | Value |
|-------|-------|
| Analysis | DOCUMENTED |
| Role | `reference_not_jobs` — category **E**; not `RawJob` ingest |
| verification_status | UNDER_REVIEW |
| access_mode | open_data |
| connector_key | — |

## Official / docs
- Official: https://www.cbs.nl/
- Docs: https://www.cbs.nl/
- Catalog note: Official statistics — import via datasets/API; do not mix incomparable series. Not wired as job connector.

## Access path (reference import)
- Preferred: CBS OData / StatLine API.
- CBS Open Data API (table keys).
- Auth: per provider (open_data).
- Series / tables: Labour force, unemployment, job vacancies (NL).

## FMI use (context KPIs — not RawJob)
- NL tightness indicators alongside live job corpus.
- Store: `provider`, `series_id`, `geo`, `time`, `value`, `vintage`, `evidence_kind`.
- Never merge into observed job KPI numerators without explicit labeling (ADR-001).

## Field map → reference facts (not RawJob)
| Source | FMI field | Notes |
|--------|-----------|-------|
| Agency series / survey row | `reference_metric` | Numeric or categorical benchmark |
| Publication date | `vintage` | Survey year or release date |
| Geography | `geo` | ISO3166 / agency code |

## Geo / compliance
- Netherlands.
- Lawful download/API only; no paywall or ToS-prohibited scraping (ADR-003).

## Gaps / next step
- Table key allowlist; Dutch/English labels.

# Cedefop Skills-OVATE (catalog_id=98)

| Field | Value |
|-------|-------|
| Analysis | DOCUMENTED |
| Role | `reference_not_jobs` — category **E**; not `RawJob` ingest |
| verification_status | UNDER_REVIEW |
| access_mode | portal |
| connector_key | — |

## Official / docs
- Official: https://www.cedefop.europa.eu/en/tools/skills-online-vacancies
- Docs: https://www.cedefop.europa.eu/en/tools/skills-online-vacancies
- Catalog note: Official statistics — import via datasets/API; do not mix incomparable series. Not wired as job connector.

## Access path (reference import)
- Preferred: Cedefop portal + downloadable research datasets (Skills-OVATE online vacancy monitor).
- Portal indicators; bulk files linked from tool pages (no FMI connector).
- Auth: per provider (portal).
- Series / tables: OVATE vacancy counts/skills demand indices by country and period.

## FMI use (context KPIs — not RawJob)
- Cross-check observed skill trends vs Cedefop OVATE; reference-only narrative in briefs.
- Store: `provider`, `series_id`, `geo`, `time`, `value`, `vintage`, `evidence_kind`.
- Never merge into observed job KPI numerators without explicit labeling (ADR-001).

## Field map → reference facts (not RawJob)
| Source | FMI field | Notes |
|--------|-----------|-------|
| Agency series / survey row | `reference_metric` | Numeric or categorical benchmark |
| Publication date | `vintage` | Survey year or release date |
| Geography | `geo` | ISO3166 / agency code |

## Geo / compliance
- EU focus.
- Lawful download/API only; no paywall or ToS-prohibited scraping (ADR-003).

## Gaps / next step
- Confirm latest bulk export URL + license before automated import.

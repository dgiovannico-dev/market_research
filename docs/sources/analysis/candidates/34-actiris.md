# Actiris (catalog_id=34)

| Field | Value |
|-------|-------|
| Analysis | PARTNER_ONLY |
| Category | A |
| verification_status | UNDER_REVIEW |
| access_mode | partner_or_unknown |
| connector_key | — |

## Official / docs
- Official PES: https://www.actiris.brussels/ — citizen search https://www.actiris.brussels/fr/citoyens/offres-d-emploi/
- Employer posting (My Actiris checklist PDF): https://www.actiris.brussels/media/qktfv2sf/creer-offre-d-emploi-avec-my-actiris.pdf — recruitment@actiris.be / 02 505 79 15
- **Labour-market statistics (not live vacancy rows):** ViewStat https://viewstat.actiris.brussels/ (offres/demande dashboards); opendata.brussels Explore **v2.1** https://opendata.brussels.be/api/explore/v2.1/console — Actiris-sourced unemployment series e.g. dataset `evolution-moyenne-annuelle-demandeurs-d-emploi-inoccupes-par-commune-genre-niveau-etudes-rbc` (no “offres d’emploi” export in catalog, Oct 2026)
- Partial BE coverage elsewhere: VDAB Vacature API https://developer.vdab.be/openservices/product/5892 (syndicated offers on Actiris site per Actiris monthly report)
- Terms / robots notes: Undocumented JSON behind the SPA is **not** an authorized connector ([ADR-003](../../decisions/ADR-003-authorized-connectors-only.md)); third-party “Actiris scraper” actors are out of scope.

## Access path (for future connector)
- Preferred: **official** Brussels vacancy bulk export or PES API (mirror VDAB) — **not published** Oct 2026
- Endpoint candidates (method + URL):
  - `GET https://opendata.brussels.be/api/explore/v2.1/catalog/datasets/{id}/records` — statistics only
  - `GET https://developer.vdab.be/services/openservices/vacatures/v4/...` — Flanders API; partial Actiris aggregation
- Auth: opendata mostly open; VDAB `X-IBM-Client-Id`
- Pagination: ODS v2.1 / VDAB per product docs

## Job list / page structure (if known)
- Content-Type: HTML/SPA search (FR/NL); no official JSON contract for external aggregators
- Citizen UI fields: title, commune/postcode, contract type, regime, date; employer often hidden on VDAB/Forem/Select syndicated rows

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| reference | source_job_id | when official API exists |
| detail URL | url | actiris.brussels |
| title (fr/nl) | title | |
| employer / KBO | company | often null on aggregated offers |
| commune | location | Brussels-Capital |
| description | description | official detail TBD |

## Geo / role fit
- Countries: BE (Brussels-Capital)
- Fit for FMI Demand Compass: Completes BE triad with VDAB + Le Forem once **lawful** machine-readable vacancy access exists

## Gaps / next step
- Request Actiris / Brussels Region open-data stewards for vacancy dataset or API (distinct from ViewStat / DEI statistics)
- Until then: VDAB open tier + Le Forem (odwb); **no** reverse-engineered search JSON

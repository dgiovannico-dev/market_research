# VDAB (catalog_id=33)

| Field | Value |
|-------|-------|
| Analysis | PARTNER_ONLY |
| Category | A |
| verification_status | UNDER_REVIEW |
| access_mode | api_key + partnership |
| connector_key | — (scaffold deferred) |

## Official / docs
- Official: https://www.vdab.be/
- Developer portal: https://developer.vdab.be/openservices/ · open-data onboarding PDF (Jan 2026)
- Vacature API CoE: https://extranet.vdab.be/api-center-excellence-coe/vacatures-ophalen-met-de-vacatures-api
- Example PDFs: GET `/vacatures`, GET `/vacatures/{id}` (extranet media, 2025-07)

## Access path (for future connector)
- Preferred: Vacature API **v4** (`…/vacatures/v4/`)
- Endpoints:
  - `GET https://api.vdab.be/services/openservices/vacatures/v4/vacatures?jobdomein={code}&postcode={pc}` → `{ aantal, resultaten[].vacatureReferentie.interneReferentie }`
  - `GET …/vacatures/{uuid}` → full vacancy
  - `GET …/vacatures/initial`, `GET …/vacatures/bulk`, `POST …/vacatures` (batch ids)
- Auth: header `X-IBM-Client-Id: <api-key>` (app registration on developer portal); OAuth/OIDC may apply on non-open tiers
- Pagination: ~15 results/page on interactive search
- **Blocker (2026):** CoE page states new Vacature API applications may be temporarily closed; full use also requires **approved partnership** + collaboration agreement for professional reuse

## Job list / page structure
- Content-Type: `application/json`
- Search list: ids only; detail has `leverancier.naam`, `publicatieDatum`, `tewerkstellingsadres`, `vrijeVereiste`, `status`, C2 occupations via Referentie API

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| `vacatureReferentie.interneReferentie` | source_job_id | UUID |
| construct detail URL / vdab site | url | |
| functie / title (detail) | title | confirm field names on live detail |
| `leverancier.naam` | company | |
| `vrijeVereiste` (+ other desc blocks) | description | |
| `tewerkstellingsadres.gemeente` + postcode | location | BE Flanders |
| `publicatieDatum` | published_at | date |

## Geo / role fit
- BE Flanders PES — complements ACTIVE `le_forem` (Wallonia) and future Actiris (Brussels)

## Gaps / next step
- Do **not** HTML-scrape vdab.be (ADR-003)
- When partnership/open-data app available: scaffold `vdab` with `VDAB_CLIENT_ID`, fail-closed, then live promote
- Until then keep catalog UNDER_REVIEW / Analysis PARTNER_ONLY

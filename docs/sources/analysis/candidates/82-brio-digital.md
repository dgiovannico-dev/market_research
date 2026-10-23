# Brio Digital (catalog_id=82)

| Field | Value |
|-------|-------|
| Analysis | PARTNER_ONLY |
| Category | C |
| verification_status | UNDER_REVIEW |
| access_mode | website_or_feed |
| connector_key | — |

## Official / docs
- Official: https://www.briodigital.io/ (UK digital/tech recruitment; **not** briodigital.com US marketing)
- Careers: https://www.briodigital.io/vacancies
- Docs / developer: none — HTML vacancies only
- Terms / robots notes: No public API; optional **direct feed** if agency offers ([ADR-003](../../decisions/ADR-003-authorized-connectors-only.md))

## Access path (for future connector)
- Preferred: client employer ATS (Greenhouse/Teamtailor/Pinpoint); no Brio bulk read API
- Endpoint candidates (method + URL): none verified
- Auth: n/a
- Pagination: n/a

## Job list / page structure (if known)
- Content-Type: HTML careers pages (`/vacancies`)

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| ATS / feed | fields | |

## Geo / role fit
- Countries: UK
- Fit for FMI Demand Compass: **Minimal** alone; merge with UK agency/ATS strategy

## Gaps / next step
- Deprecate or merge if no feed in 12 months
- No scraper without contract

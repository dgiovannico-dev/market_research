# XING Jobs (catalog_id=29)

| Field | Value |
|-------|-------|
| Analysis | PARTNER_ONLY |
| Category | A |
| verification_status | NEEDS_CREDENTIALS |
| access_mode | partner_api |
| connector_key | — |

## Official / docs
- Official: https://www.xing.com/jobs
- Developer: XING / New Work SE developer program (OAuth; job APIs for approved apps).
- Terms: developer agreement; bulk redistribution restricted.

## Access path (for future connector)
- Preferred: register app at XING developer portal; request job-related scopes.
- Endpoint candidates: REST resources documented for partners (job search/posting — confirm current API catalog).
- Auth: OAuth 2.0 client + user or server token per product.
- Pagination: cursor/limit per API docs.

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| id | source_job_id | |
| link | url | DACH professional |

## Geo / role fit
- Countries: DE/AT/CH primary.
- Fit for FMI Demand Compass: **Medium** for DACH demand — after developer approval.

## Gaps / next step
- Apply for partner/developer access; no HTML scrape ([ADR-003](../../decisions/ADR-003-authorized-connectors-only.md)).

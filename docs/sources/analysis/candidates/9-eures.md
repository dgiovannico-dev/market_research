# EURES (catalog_id=9)

| Field | Value |
|-------|-------|
| Analysis | PARTNER_ONLY |
| Category | A |
| verification_status | NEEDS_CREDENTIALS |
| access_mode | partner_api |
| connector_key | — |

## Official / docs
- Official: https://eures.europa.eu/
- Developer: EC / EURES technical documentation for registered PES and partner organisations (not a self-serve public job-search API).
- Terms: EU mobility data; redistribution typically limited to authorised employment-service use.

## Access path (for future connector)
- Preferred: partner API after registration with a national PES or approved EURES partner role.
- Endpoint candidates: documented EURES web services / job-vacancy exchange endpoints (tenant-specific base URL; confirm current spec with EC contact).
- Auth: organisation credentials issued after onboarding.
- Pagination: per service spec (often batch or cursor by vacancy id).

## Job list / page structure (if known)
- Public site: HTML search; not an ADR-003 ingest path.
- Partner feeds: structured vacancy objects (title, employer, location, occupation codes).

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| vacancy id | source_job_id | |
| application URL | url | |
| title | title | |
| employer | company | |
| NUTS / country | location, country | strong EU geo fit |

## Geo / role fit
- Countries: EU/EEA + mobility corridors; high value for cross-border demand signals.
- Fit for FMI Demand Compass: **Yes, if partner access** — complements national PES connectors (Arbetsförmedlingen, France Travail, etc.).

## Gaps / next step
- Identify whether FMI qualifies as research vs PES; request EC/EURES partner onboarding.
- Do not scrape eures.europa.eu ([ADR-003](../../decisions/ADR-003-authorized-connectors-only.md)).

# O*NET Web Services (catalog_id=150)

| Field | Value |
|-------|-------|
| Analysis | TODO_ACCESS |
| Category | G |
| verification_status | NEEDS_CREDENTIALS |
| access_mode | api_key |
| connector_key | — |

## Official / docs
- Official: https://services.onetcenter.org/
- Developer: O*NET Web Services v2 (free registration for username/password).
- Terms: US DOL taxonomy; occupation/skills metadata — not job listings.

## Access path (for future connector)
- Preferred: REST calls to occupation/summary endpoints post-registration.
- Auth: Basic auth with issued credentials.
- Use: taxonomy enrichment (ESCO/O*NET crosswalk), not RawJob source.

## Geo / role fit
- Countries: US-centric occupation taxonomy.
- Fit for FMI Demand Compass: **Taxonomy enrichment** — pursue registration for classification quality.

## Gaps / next step
- Register at onetcenter.org; store creds in env; separate from job collectors.

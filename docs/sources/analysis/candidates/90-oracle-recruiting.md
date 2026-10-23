# Oracle Recruiting (catalog_id=90)

| Field | Value |
|-------|-------|
| Analysis | PARTNER_ONLY |
| Category | D |
| verification_status | NEEDS_CREDENTIALS |
| access_mode | enterprise |
| connector_key | — |

## Official / docs
- Official: https://www.oracle.com/human-capital-management/recruiting/
- Developer: Oracle Fusion HCM REST (recruiting job requisitions) on customer pod.
- Terms: cloud customer credentials required.

## Access path (for future connector)
- Preferred: HCM REST `recruitingJobRequisitions` (exact resource per Oracle docs on customer instance).
- Auth: OAuth / IDCS for integration user.
- Pagination: REST pagination headers.

## Geo / role fit
- Fit for FMI Demand Compass: **Enterprise tenant only** — not a public aggregator source.

## Gaps / next step
- Skip global enablement; note for customer-specific projects.

# iCIMS (catalog_id=91)

| Field | Value |
|-------|-------|
| Analysis | PARTNER_ONLY |
| Category | D |
| verification_status | NEEDS_CREDENTIALS |
| access_mode | enterprise |
| connector_key | — |

## Official / docs
- Official: https://www.icims.com/
- Developer: iCIMS REST API for customer instances (job portal API where enabled).
- Terms: customer-issued credentials.

## Access path (for future connector)
- Preferred: customer API base URL + key for job search endpoint (instance-specific).
- Auth: API key / OAuth per iCIMS admin.

## Geo / role fit
- Fit for FMI Demand Compass: **Tenant-scoped** — complements generic ATS board collector for public career sites where iCIMS hosts public boards.

## Gaps / next step
- Prefer public board URLs via existing ATS boards collector when exposed; API only with customer contract.

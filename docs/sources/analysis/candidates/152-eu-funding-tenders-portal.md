# EU Funding & Tenders Portal (catalog_id=152)

| Field | Value |
|-------|-------|
| Analysis | TODO_ACCESS |
| Category | H |
| verification_status | UNDER_REVIEW |
| access_mode | open_data_or_portal |
| connector_key | — |

## Official / docs
- Official: https://ec.europa.eu/info/funding-tenders/opportunities/portal/
- Docs / developer: https://ec.europa.eu/info/funding-tenders/opportunities/portal/
- Terms / robots notes: Use only authorized APIs/open data; procurement ≠ job postings (ADR-003).

## Access path (for future connector)
- Preferred: portal API (Funding & Tenders)
- Endpoint candidates (method + URL):
  - EU Funding & Tenders Portal API (SEDIA): search calls for grants/tenders
  - https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/support/apis
- Auth: Account + API token for programmatic search
- Pagination: Portal page index / API offset

## Job list / page structure (if known)
- Content-Type: varies
- Structure: JSON opportunity records

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| title, deadline, budget | funding/tender | Not employment contracts |

## Geo / role fit
- Countries: EU programmes
- Fit for FMI Demand Compass: reference, FX, taxonomy, procurement context, or import — **not** primary vacancy KPIs unless explicitly jobs.

## Gaps / next step
- Credentials + ToS review before connector.

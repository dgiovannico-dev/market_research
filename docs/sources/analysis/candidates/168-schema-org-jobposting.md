# Schema.org JobPosting (catalog_id=168)

| Field | Value |
|-------|-------|
| Analysis | DOCUMENTED |
| Category | I |
| verification_status | VALIDATED |
| access_mode | standard |
| connector_key | — |

## Official / docs
- Official: https://schema.org/JobPosting
- Docs / developer: https://schema.org/JobPosting
- Terms / robots notes: Use only authorized APIs/open data; procurement ≠ job postings (ADR-003).

## Access path (for future connector)
- Preferred: standard schema
- Endpoint candidates (method + URL):
  - https://schema.org/JobPosting (JSON-LD spec)
- Auth: N/A
- Pagination: N/A

## Job list / page structure (if known)
- Content-Type: varies
- Structure: JSON-LD JobPosting on publisher pages

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| title, datePosted, hiringOrganization | RawJob mapping template | Normalization target |

## Geo / role fit
- Countries: Global publishers
- Fit for FMI Demand Compass: reference, FX, taxonomy, procurement context, or import — **not** primary vacancy KPIs unless explicitly jobs.

## Gaps / next step
- Only where publishers expose JSON-LD lawfully; no bulk scrape of aggregators.

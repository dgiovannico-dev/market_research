# UK Find a Tender (catalog_id=154)

| Field | Value |
|-------|-------|
| Analysis | DOCUMENTED |
| Category | H |
| verification_status | UNDER_REVIEW |
| access_mode | open_data_or_portal |
| connector_key | — |

## Official / docs
- Official: https://www.find-tender.service.gov.uk/
- Docs / developer: https://www.find-tender.service.gov.uk/
- Terms / robots notes: Use only authorized APIs/open data; procurement ≠ job postings (ADR-003).

## Access path (for future connector)
- Preferred: open data (OCDS)
- Endpoint candidates (method + URL):
  - GET https://www.find-tender.service.gov.uk/api/1.0/ocdsReleasePackages?limit=…
  - Bulk release packages (FTS post-Brexit)
- Auth: None for public releases
- Pagination: cursor / `updatedFrom` filters

## Job list / page structure (if known)
- Content-Type: varies
- Structure: OCDS release packages

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| releases[].tender | procurement | Adjacent signal |

## Geo / role fit
- Countries: UK
- Fit for FMI Demand Compass: reference, FX, taxonomy, procurement context, or import — **not** primary vacancy KPIs unless explicitly jobs.

## Gaps / next step
- High volume; filter CPV/SME relevant to IT services.

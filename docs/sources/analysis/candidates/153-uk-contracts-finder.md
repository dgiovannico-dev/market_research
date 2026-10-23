# UK Contracts Finder (catalog_id=153)

| Field | Value |
|-------|-------|
| Analysis | DOCUMENTED |
| Category | H |
| verification_status | UNDER_REVIEW |
| access_mode | open_data_or_portal |
| connector_key | — |

## Official / docs
- Official: https://www.contractsfinder.service.gov.uk/
- Docs / developer: https://www.contractsfinder.service.gov.uk/
- Terms / robots notes: Use only authorized APIs/open data; procurement ≠ job postings (ADR-003).

## Access path (for future connector)
- Preferred: open data REST
- Endpoint candidates (method + URL):
  - GET https://www.contractsfinder.service.gov.uk/Published/Notices/OCDS/Search (OCDS search)
  - Published notice feeds documented on site
- Auth: None for published notices
- Pagination: PublishedFrom/PublishedTo, page size

## Job list / page structure (if known)
- Content-Type: varies
- Structure: OCDS JSON releases

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| tender.title, value | procurement | Context only |

## Geo / role fit
- Countries: UK
- Fit for FMI Demand Compass: reference, FX, taxonomy, procurement context, or import — **not** primary vacancy KPIs unless explicitly jobs.

## Gaps / next step
- Build OCDS→internal tender model; not RawJob.

# Open Contracting Data Standard (catalog_id=161)

| Field | Value |
|-------|-------|
| Analysis | DOCUMENTED |
| Category | H |
| verification_status | UNDER_REVIEW |
| access_mode | open_data_or_portal |
| connector_key | — |

## Official / docs
- Official: https://standard.open-contracting.org/
- Docs / developer: https://standard.open-contracting.org/
- Terms / robots notes: Use only authorized APIs/open data; procurement ≠ job postings (ADR-003).

## Access path (for future connector)
- Preferred: standard (OCDS JSON Schema)
- Endpoint candidates (method + URL):
  - Schema + release/record model: https://standard.open-contracting.org/latest/en/schema/
- Auth: N/A
- Pagination: N/A (format spec)

## Job list / page structure (if known)
- Content-Type: varies
- Structure: OCDS release/record JSON

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| tender, awards, parties | normalized procurement | Mapper target for H sources |

## Geo / role fit
- Countries: Global standard
- Fit for FMI Demand Compass: reference, FX, taxonomy, procurement context, or import — **not** primary vacancy KPIs unless explicitly jobs.

## Gaps / next step
- Implement shared OCDS importer before per-portal parsers.

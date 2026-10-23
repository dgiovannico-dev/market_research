# Public APIs (catalog_id=163)

| Field | Value |
|-------|-------|
| Analysis | DOCUMENTED |
| Category | I |
| verification_status | VALIDATED |
| access_mode | directory |
| connector_key | — |

## Official / docs
- Official: https://github.com/public-apis/public-apis
- Docs / developer: https://github.com/public-apis/public-apis
- Terms / robots notes: Use only authorized APIs/open data; procurement ≠ job postings (ADR-003).

## Access path (for future connector)
- Preferred: directory (GitHub README)
- Endpoint candidates (method + URL):
  - https://github.com/public-apis/public-apis (curated list)
- Auth: N/A
- Pagination: N/A

## Job list / page structure (if known)
- Content-Type: varies
- Structure: Markdown tables by category

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| N/A — human discovery |

## Geo / role fit
- Countries: Global
- Fit for FMI Demand Compass: reference, FX, taxonomy, procurement context, or import — **not** primary vacancy KPIs unless explicitly jobs.

## Gaps / next step
- Manual vetting per ADR-003 before any connector.

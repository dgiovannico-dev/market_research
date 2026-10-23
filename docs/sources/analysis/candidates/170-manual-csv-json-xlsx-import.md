# Manual CSV/JSON/XLSX Import (catalog_id=170)

| Field | Value |
|-------|-------|
| Analysis | DOCUMENTED |
| Category | I |
| verification_status | ACTIVE |
| access_mode | manual_import |
| connector_key | manual_import |

**Already covered:** [`../manual_import.md`](../manual_import.md) — operator upload path.

## Official / docs
- Official: https://localhost/manual
- Docs / developer: https://localhost/manual
- Terms / robots notes: Use only authorized APIs/open data; procurement ≠ job postings (ADR-003).

## Access path (for future connector)
- Preferred: manual_import
- Endpoint candidates (method + URL):
  - In-app/API upload of CSV, JSON, XLSX (no remote URL)
- Auth: App auth for operators
- Pagination: Batch rows

## Job list / page structure (if known)
- Content-Type: varies
- Structure: Tabular columns → ingest mapper

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| operator columns | RawJob fields | Quality = source file |

## Geo / role fit
- Countries: User-defined
- Fit for FMI Demand Compass: reference, FX, taxonomy, procurement context, or import — **not** primary vacancy KPIs unless explicitly jobs.

## Gaps / next step
- Validate schema; sample at `data/samples/jobs_sample.csv`.

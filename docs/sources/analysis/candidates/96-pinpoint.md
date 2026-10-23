# Pinpoint (catalog_id=96)

| Field | Value |
|-------|-------|
| Analysis | IMPLEMENTED |
| Category | D |
| verification_status | ACTIVE |
| access_mode | public_api_per_company |
| connector_key | `pinpoint` |
| Collector sheet | [../pinpoint.md](../pinpoint.md) |

## Official / docs
- Official: https://www.pinpointhq.com/
- Docs / developer: https://developers.pinpointhq.com/docs/jobs-json-endpoint — public `postings.json`; https://developers.pinpointhq.com/reference/get-jobs for authenticated JSON:API.
- Terms / robots notes: Public feed is CORS-friendly and keyless; authenticated API must not be exposed client-side.

## Access path (for future connector)
- Preferred: public `postings.json` per subdomain (replaces legacy `jobs.json` when multiple postings per job).
- Endpoint candidates (method + URL):
  - `GET https://{subdomain}.pinpointhq.com/postings.json` — array in `data[]`.
  - Optional filters: `department_id`, `division_id`, `location_id`, `location_city_state_name` (comma = OR within filter; AND across filters).
  - Legacy: `GET https://{subdomain}.pinpointhq.com/jobs.json` (one default posting per job only).
- Auth: none on `postings.json`.
- Pagination: full list in one response for typical boards (verify large employers).

## Job list / page structure (if known)
- Content-Type: `application/json`
- Path to items: `data[]`
- Key fields: `id`, `title`, `url`, `location`, `department`, `description`, `compensation`, `compensation_minimum` / `_maximum`, `compensation_currency`.

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| `id` | source_job_id | subdomain prefix |
| `url` | url | |
| `title` | title | |
| subdomain or embedded org name | company | |
| `description` | description | HTML |
| `location` | location | |
| — | published_at | not on public feed per third-party surveys; optional detail API |
| compensation / remote flags | raw + remote_hint | partial coverage |

## Geo / role fit
- Countries: UK-weighted; growing EU/US employers on Pinpoint.
- Fit for FMI Demand Compass: good structured pay fields when present; tenant list driven (`PINPOINT_SUBDOMAINS`).

## Gaps / next step
- Standardize on `postings.json`; document probe (`workwithus.pinpointhq.com` returns 200).
- Add collector sibling to `ats_boards.py` with per-tenant cap.
- JSON:API with API key = PARTNER_ONLY per customer.

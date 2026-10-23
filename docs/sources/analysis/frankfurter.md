# Frankfurter (`frankfurter`)

| Field | Value |
|-------|-------|
| Analysis | DONE |
| collection_mode | n/a (FX helper) |
| Role | FX rates overlay — **not** a job ingest source |
| Probed_at | 2026-10-21 |

## Endpoint

- **URL:** `GET https://api.frankfurter.app/latest` (and historical paths)
- **Auth:** none
- **Product path:** `/api/v1/fx/rates` in this repo

## Payload

- JSON FX rates keyed by currency code; used for salary normalization, not `RawJob`.

## Gaps

- Not a job list; keep out of crawl schedulers as a job collector.

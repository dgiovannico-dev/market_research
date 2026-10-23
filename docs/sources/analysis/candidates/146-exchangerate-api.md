# ExchangeRate-API (catalog_id=146)

| Field | Value |
|-------|-------|
| Analysis | TODO_ACCESS |
| Category | G |
| verification_status | NEEDS_CREDENTIALS |
| access_mode | api_key |
| connector_key | — |

## Official / docs
- Official: https://www.exchangerate-api.com/
- Developer: v6 REST docs on site (`/v6/{API_KEY}/latest/{BASE}`).
- Terms: free tier limited; production key required.

## Access path (for future connector)
- Preferred: HTTPS GET latest rates endpoint per docs.
- Auth: path or header API key (per tier documentation).

## Geo / role fit
- FX reference only; not job ingest.

## Gaps / next step
- Optional alternate to Open Exchange Rates; low priority if Frankfurter suffices.

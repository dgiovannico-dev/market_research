# Open Exchange Rates (catalog_id=144)

| Field | Value |
|-------|-------|
| Analysis | TODO_ACCESS |
| Category | G |
| verification_status | NEEDS_CREDENTIALS |
| access_mode | api_key |
| connector_key | — |

## Official / docs
- Official: https://openexchangerates.org/
- Developer: https://docs.openexchangerates.org/
- Terms: App ID required; not a job connector — optional FX overlay ([CREDENTIALED_CONNECTORS](../CREDENTIALED_CONNECTORS.md)).

## Access path (for future connector)
- Preferred: `GET https://openexchangerates.org/api/latest.json?app_id={APP_ID}`
- Auth: query param `app_id` (`OPEN_EXCHANGE_RATES_APP_ID`).
- Note: Frankfurter/ECB remain primary in FMI.

## Geo / role fit
- Fit for FMI Demand Compass: **FX utility only** — enable if richer currency coverage needed.

## Gaps / next step
- Set env in `.env.example`; wire already documented on `GET /api/v1/fx/rates` overlay.

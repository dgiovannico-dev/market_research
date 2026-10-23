# Programmable Search Engine (catalog_id=165)

| Field | Value |
|-------|-------|
| Analysis | TODO_ACCESS |
| Category | I |
| verification_status | NEEDS_CREDENTIALS |
| access_mode | api_key |
| connector_key | — |

## Official / docs
- Official: https://programmablesearchengine.google.com/
- Developer: Custom Search JSON API (`https://www.googleapis.com/customsearch/v1`).
- Terms: Google Cloud API key + search engine ID; discovery aid only — not a job board.

## Access path (for future connector)
- Preferred: `GET customsearch/v1?key={API_KEY}&cx={CX}&q={query}`
- Auth: API key + programmable engine ID.
- Use: source discovery / URL watchlist — not ADR-003 substitute for authorized job APIs.

## Geo / role fit
- Fit for FMI Demand Compass: **Research/discovery tooling** — optional; quota/cost aware.

## Gaps / next step
- Document in ops/research flows only; do not treat CSE results as verified job evidence without following authorized connector on target site.

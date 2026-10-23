# La Fosse (catalog_id=81)

| Field | Value |
|-------|-------|
| Analysis | PARTNER_ONLY |
| Category | C |
| verification_status | UNDER_REVIEW |
| access_mode | website_or_feed |
| connector_key | — |

## Official / docs
- Official: https://www.lafosse.com/ (UK digital/tech recruitment boutique)
- Docs / developer: no public job export API
- Terms / robots notes: Web job list; **direct feed or client ATS** only ([ADR-003](../../decisions/ADR-003-authorized-connectors-only.md))

## Access path (for future connector)
- Preferred: La Fosse **partnership/syndication** if offered; Greenhouse/Teamtailor UK clients
- Endpoint candidates (method + URL): none verified
- Auth: n/a
- Pagination: n/a

## Job list / page structure (if known)
- Content-Type: HTML careers/search

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| licensed feed | fields | |

## Geo / role fit
- Countries: UK (London digital/tech)
- Fit for FMI Demand Compass: **Low standalone** — dedupe with UK ATS boards

## Gaps / next step
- Feed inquiry to La Fosse; no scrape without contract

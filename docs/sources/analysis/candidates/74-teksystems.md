# TEKsystems (catalog_id=74)

| Field | Value |
|-------|-------|
| Analysis | PARTNER_ONLY |
| Category | C |
| verification_status | UNDER_REVIEW |
| access_mode | website_or_feed |
| connector_key | — |

## Official / docs
- Official: https://www.teksystems.com/en/ (Allegis Group brand)
- Privacy: https://www.teksystems.com/en/privacy-notices — no published **public job export API** for third-party aggregators Oct 2026
- Jobs hosted on Allegis career search / regional TEKsystems sites (HTML)
- Terms / robots notes: No verified open bulk API; treat as **partner feed or employer ATS** path only ([ADR-003](../../decisions/ADR-003-authorized-connectors-only.md))

## Access path (for future connector)
- Preferred: Allegis Group **enterprise data/syndication** agreement; client employer public ATS boards
- Endpoint candidates (method + URL): none public for market-wide job JSON
- Auth: n/a until partnership
- Pagination: n/a

## Job list / page structure (if known)
- Content-Type: HTML job search; US-heavy IT staffing

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| licensed feed | fields | |

## Geo / role fit
- Countries: US primary; global Allegis footprint
- Fit for FMI Demand Compass: **Low–medium** unless feed licensed; many roles on client boards

## Gaps / next step
- Allegis digital/partner desk for XML/API terms
- No unauthorized harvest of teksystems.com listings

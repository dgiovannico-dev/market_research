# Computer Futures (catalog_id=78)

| Field | Value |
|-------|-------|
| Analysis | BLOCKED_TOS |
| Category | C |
| verification_status | REJECTED |
| access_mode | website_or_feed |
| connector_key | — |

## Official / docs
- Official: https://www.computerfutures.com/ (**Hays** brand — IT contract/permanent)
- **Terms:** Hays group scrape prohibition — e.g. https://www.hays.nl/en/terms-of-use (“No … **scraping** or other manipulation of the content”); applies to Hays-owned brands
- Docs / developer: no public API; same constraints as Hays (67)
- Terms / robots notes: IT staffing web search only ([ADR-003](../../decisions/ADR-003-authorized-connectors-only.md))

## Access path (for future connector)
- Preferred: Hays group **license** (shared with 67); client ATS boards
- Endpoint candidates (method + URL): none authorized public
- Auth: n/a
- Pagination: n/a

## Job list / page structure (if known)
- Content-Type: HTML regional Computer Futures sites

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| licensed / ATS | fields | |

## Geo / role fit
- Countries: UK, DE, US, APAC IT markets
- Fit for FMI Demand Compass: IT contract demand via **employer connectors**, not CF scrape

## Gaps / next step
- Merge outreach with Hays (67); no separate scraper

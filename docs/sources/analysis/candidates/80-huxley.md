# Huxley (catalog_id=80)

| Field | Value |
|-------|-------|
| Analysis | BLOCKED_TOS |
| Category | C |
| verification_status | REJECTED |
| access_mode | website_or_feed |
| connector_key | — |

## Official / docs
- Official: https://www.huxley.com/ (**Hays** brand — banking, finance, tech contract)
- **Terms:** Hays group — no scraping/harvesting https://www.hays.nl/en/terms-of-use (same as 67, 78)
- Docs / developer: none for public bulk API
- Terms / robots notes: Regional Huxley sites; banking clients often on Workday/SuccessFactors externally ([ADR-003](../../decisions/ADR-003-authorized-connectors-only.md))

## Access path (for future connector)
- Preferred: Hays group license; **employer ATS** for finance-tech roles
- Endpoint candidates (method + URL): none public
- Auth: n/a
- Pagination: n/a

## Job list / page structure (if known)
- Content-Type: HTML job listings

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| ATS / license | fields | |

## Geo / role fit
- Countries: UK, EU financial centers
- Fit for FMI Demand Compass: Finance-tech crossover via client boards, not Huxley scrape

## Gaps / next step
- Joint outreach with Hays (67); no scraper

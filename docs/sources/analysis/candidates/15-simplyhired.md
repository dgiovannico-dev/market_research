# SimplyHired (catalog_id=15)

| Field | Value |
|-------|-------|
| Analysis | BLOCKED_TOS |
| Category | A |
| verification_status | UNDER_REVIEW |
| access_mode | unknown |
| connector_key | — |

## Official / docs
- Official: https://www.simplyhired.com/
- Docs / developer: Historical Job-a-matic XML API discontinued 2014; Simply-Partner program terminated June 2016 (no replacement public job API documented)
- Terms / robots notes: Commercial aggregator; legacy publisher API shut down. Third-party scraper APIs are not authorized sources under ADR-003.

## Access path (for future connector)
- Preferred: none suitable without new official publisher program
- Endpoint candidates (method + URL): none verified for 2026 consumer ingest
- Auth: N/A
- Pagination: N/A

## Job list / page structure (if known)
- Content-Type: N/A (no authorized bulk access)
- Path to items / selectors: public website only — not an approved connector path
- Key fields observed or documented: site search UI only

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| — | — | No authorized mapping |

## Geo / role fit
- Countries: US-focused history; site presents multi-country search today
- Fit for FMI Demand Compass: Defer; use Adzuna, Careerjet, or other authorized aggregators instead

## Gaps / next step
- Mark catalog `BLOCKED` or keep UNDER_REVIEW until Talent/Recruit publishes a new authorized data program
- Do not implement HTML or unofficial API scraping

# Kforce (catalog_id=75)

| Field | Value |
|-------|-------|
| Analysis | BLOCKED_TOS |
| Category | C |
| verification_status | REJECTED |
| access_mode | website_or_feed |
| connector_key | — |

## Official / docs
- Official: https://www.kforce.com/
- **Terms of Use:** https://www.kforce.com/terms-of-use — Materials may not be “copied, distributed, downloaded … **reused, republished** … or otherwise used **without the express written permission** of Kforce”; site for personal job search, not commercial redistribution
- Careers portal: https://myhiring.kforce.com/ (Oracle Taleo-style; authenticated candidate flows)
- Docs / developer: no public job listings API
- Terms / robots notes: Commercial aggregation/scrape not permitted ([ADR-003](../../decisions/ADR-003-authorized-connectors-only.md))

## Access path (for future connector)
- Preferred: Kforce **written** data license
- Endpoint candidates (method + URL): none public
- Auth: n/a
- Pagination: n/a

## Job list / page structure (if known)
- Content-Type: HTML + myhiring portal

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| licensed export | fields | |

## Geo / role fit
- Countries: US IT/finance staffing
- Fit for FMI Demand Compass: **Low** unless licensed; US public boards cover overlap

## Gaps / next step
- No kforce.com scraper; partner inquiry if US staffing slice needed

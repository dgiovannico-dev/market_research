# Robert Walters (catalog_id=76)

| Field | Value |
|-------|-------|
| Analysis | BLOCKED_TOS |
| Category | C |
| verification_status | REJECTED |
| access_mode | website_or_feed |
| connector_key | — |

## Official / docs
- Official: https://www.robertwalters.com/ (UK, FR, BE, NL, DE, APAC)
- **Marketplace / portal terms (FR PDF):** https://www.robertwalters.fr/content/dam/robert-walters-redesign/country/france/files/policies/RWC%20Marketplace%20process%20and%20terms%20of%20use.pdf — may not “**systematically retrieve data** … to create or compile … a **database or directory** without written permission”; no unauthorized automated collection; PerimeterX on public search (third-party bypass tools not authorized)
- Docs / developer: no public job API for aggregators
- Terms / robots notes: Recruitment agency listings; employer often confidential ([ADR-003](../../decisions/ADR-003-authorized-connectors-only.md))

## Access path (for future connector)
- Preferred: Robert Walters **written** syndication license
- Endpoint candidates (method + URL): none public
- Auth: n/a
- Pagination: n/a

## Job list / page structure (if known)
- Content-Type: HTML per market; consultant-centric metadata

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| licensed feed | fields | |

## Geo / role fit
- Countries: UK, FR, BE, NL, DE, APAC
- Fit for FMI Demand Compass: Finance/professional niche; **no scrape**

## Gaps / next step
- RW data partnership if needed; prefer employer ATS for underlying roles

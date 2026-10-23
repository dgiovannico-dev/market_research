# Experis (catalog_id=73)

| Field | Value |
|-------|-------|
| Analysis | BLOCKED_TOS |
| Category | C |
| verification_status | REJECTED |
| access_mode | website_or_feed |
| connector_key | — |

## Official / docs
- Official: https://www.experis.com/ (ManpowerGroup IT staffing)
- **Terms:** ManpowerGroup site terms apply — no spiders/scrapers/data mining without consent https://www.manpowergroup.com/en/policies/terms-of-use (see also Manpower 72)
- Docs / developer: no public Experis job bulk API
- Terms / robots notes: IT/engineering roles often duplicated on client Greenhouse/Workday ([ADR-003](../../decisions/ADR-003-authorized-connectors-only.md))

## Access path (for future connector)
- Preferred: ManpowerGroup/Experis **licensed export**; ingest at end-client ATS
- Endpoint candidates (method + URL): none verified public
- Auth: n/a
- Pagination: n/a

## Job list / page structure (if known)
- Content-Type: HTML US/EU localized search

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| client ATS | fields | preferred path |

## Geo / role fit
- Countries: US, UK, DE, FR, Nordics
- Fit for FMI Demand Compass: IT contract signal via **employer boards**, not Experis scrape

## Gaps / next step
- Watchlist Experis clients with public ATS tenants
- Syndication policy inquiry via ManpowerGroup digital

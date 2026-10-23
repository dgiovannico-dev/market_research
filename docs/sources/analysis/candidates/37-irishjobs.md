# IrishJobs (catalog_id=37)

| Field | Value |
|-------|-------|
| Analysis | BLOCKED_TOS |
| Category | A |
| verification_status | UNDER_REVIEW |
| access_mode | unknown |
| connector_key | — |

## Official / docs
- Official: https://www.irishjobs.ie/
- Docs / developer: No public job search API or RSS documented (StepStone/Irish Jobs Group)
- Terms / robots notes: Commercial board; third-party scrapers explicitly warn about ToS. No authorized bulk path under ADR-003.

## Access path (for future connector)
- Preferred: partner API if StepStone Ireland offers affiliate feed (not found publicly)
- Endpoint candidates (method + URL): none verified
- Auth: N/A
- Pagination: N/A

## Job list / page structure (if known)
- Content-Type: HTML/JS search application
- Path to items / selectors: public UI only
- Key fields observed or documented: salary bands, location (IE counties), contract type on detail pages

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| — | — | No authorized mapping |

## Geo / role fit
- Countries: IE
- Fit for FMI Demand Compass: Low until partner feed; consider EU-wide aggregators with IE filter (Adzuna, Careerjet) where authorized

## Gaps / next step
- Ask StepStone/IrishJobs partner team for XML/JSON export (mirror UK Reed jobseeker API if exists for IE)
- Do not implement HTML or residential-proxy scraping

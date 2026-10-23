# Harvey Nash (catalog_id=77)

| Field | Value |
|-------|-------|
| Analysis | PARTNER_ONLY |
| Category | C |
| verification_status | UNDER_REVIEW |
| access_mode | website_or_feed |
| connector_key | — |

## Official / docs
- Official: https://www.harveynash.com/ (Nash Squared group — IT recruitment & outsourcing)
- Privacy (US): https://www.harveynashusa.com/privacy-policy — cookies/analytics; **no public job export API** documented
- Regional sites (UK/US/EU) — HTML job search; bot challenges on forms (reCAPTCHA on UK properties)
- Terms / robots notes: No verified bulk API; no explicit scrape recipe without Nash Squared contract ([ADR-003](../../decisions/ADR-003-authorized-connectors-only.md))

## Access path (for future connector)
- Preferred: Nash Squared / Harvey Nash **data partnership**; client employer ATS (IT roles)
- Endpoint candidates (method + URL): none public Oct 2026
- Auth: n/a
- Pagination: n/a

## Job list / page structure (if known)
- Content-Type: HTML listings; IT/ digital focus

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| licensed export | fields | |

## Geo / role fit
- Countries: UK, US, EU
- Fit for FMI Demand Compass: IT outsourcing/recruitment signal **if** feed licensed

## Gaps / next step
- Group digital team syndication inquiry
- Do not automate public search without contract

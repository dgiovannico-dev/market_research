# Flexiple (catalog_id=66)

| Field | Value |
|-------|-------|
| Analysis | BLOCKED_TOS |
| Category | B |
| verification_status | UNDER_REVIEW |
| access_mode | unknown |
| connector_key | — |

## Official / docs
- Official: https://flexiple.com/
- Docs / developer: No public developer portal, OpenAPI, RSS, or job JSON feed (verified 2026-10-21).
- Terms / robots notes: Curated vetted-freelancer network; client/talent flows are web/app login. No authorized bulk listing export (ADR-003).

## Access path (for future connector)
- Preferred: enterprise/partner data agreement if offered.
- Endpoint candidates (method + URL): none documented.
- Auth: N/A for public job index.
- Pagination: N/A.

## Job list / page structure (if known)
- Content-Type: marketing site + gated hiring workflow; no searchable public job board comparable to Freelancer/Upwork APIs.
- Roles may appear on employer ATS boards we already support (Greenhouse, Lever, etc.) rather than on Flexiple as open listings.

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| — | — | Pending authorized access path |

## Geo / role fit
- Countries: global remote; India/US/EU presence in marketing.
- Fit for FMI Demand Compass: **Low** until lawful bulk access; category B overlap with Toptal-style curated networks (see `46-toptal.md` PARTNER_ONLY).

## Gaps / next step
- Outreach for partnership or client export format; do not implement HTML scraper.
- Mirror demand via employer ATS connectors where Flexiple-placed roles are posted publicly.

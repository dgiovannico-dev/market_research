# NAV (catalog_id=41)

| Field | Value |
|-------|-------|
| Analysis | DONE |
| Category | A |
| verification_status | ACTIVE |
| access_mode | public_api |
| connector_key | `nav_stilling_feed` |

## Official / docs
- Official: https://www.nav.no/ (job search: arbeidsplassen.nav.no)
- Docs / developer: https://navikt.github.io/pam-stilling-feed/ ; data.norge.no dataset “API - NAVs stillingsdatabase”
- Terms / robots notes: Feed requires JWT; agree to terms. Experimental public token at `/api/publicToken` (rotates; ~35d TTL observed). Private token via email nav.team.arbeidsplassen@nav.no. Excludes Finn.no listings.

## Access path (connector)
- Dump: `nav_stilling_feed` → JWT from `GET /api/publicToken`, then `GET /api/v1/feed` with `If-Modified-Since` (lookback window) + follow relative `next_url` (capped)
- Optional tip: `GET /api/v1/feed?last=true`
- Detail (not fetched in thin collector): `GET /api/v1/feedentry/{uuid}` → `ad_content` for full HTML description
- Alternate search (ACTIVE): `nav_arbeidsplassen` → `GET https://arbeidsplassen.nav.no/stillinger/api/search`
- Auth: `Authorization: Bearer {JWT}`

## Job list / page structure
- Content-Type: `application/json` feed (probed 200 with public token Oct 2026)
- Default `/api/v1/feed` starts at historical INACTIVE (~2019/2023); use `If-Modified-Since` (correct RFC-1123 weekday) or `?last=true`
- Items: `id`, `url` (relative feedentry), `title`, `date_modified`, `_feed_entry.{uuid,status,title,businessName,municipal,sistEndret}`
- ACTIVE feedentry returns `ad_content` (full ad JSON); INACTIVE returns stripped `{uuid,status,sistEndret}`

## Field map → RawJob (thin dump)
| Source | RawJob | Notes |
|--------|--------|-------|
| `_feed_entry.uuid` | source_job_id | same UUID as search API |
| — | url | `https://arbeidsplassen.nav.no/stillinger/stilling/{uuid}` |
| `_feed_entry.title` | title | |
| `_feed_entry.businessName` | company | |
| — | description | omitted in thin dump (no N+1 feedentry) |
| `_feed_entry.municipal` | location | `"{municipal}, Norway"` |
| `date_modified` | published_at | |

## Geo / role fit
- Countries: NO
- Fit for FMI Demand Compass: High — feed is dump/sync; search covers query mode

## Dedupe vs `nav_arbeidsplassen`
- Same vacancy UUID and same stilling URL → ingest merges on `canonical_url` across sources
- Search is query-capped; feed is time-window ACTIVE dump (`dump_complete=false`)

## Gaps / next step
- Register private feed consumer for production (stable token)
- Optional: enrich ACTIVE items via feedentry `ad_content` (description / remote / tags) under a detail budget

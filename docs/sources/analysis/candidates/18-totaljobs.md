# Totaljobs (catalog_id=18)

| Field | Value |
|-------|-------|
| Analysis | PARTNER_ONLY |
| Category | A |
| verification_status | UNDER_REVIEW |
| access_mode | unknown |
| connector_key | — |

## Official / docs
- Official: https://www.totaljobs.com/
- Docs / developer: https://api.stepstone.com/knowledge-base/totaljobs-uk/ (StepStone XML **posting** guide for recruiters)
- Terms / robots notes: Documented integration is **employer → board** XML job load, not jobseeker bulk download. Feed credentials from account manager.

## Access path (for future connector)
- Preferred: partner feed (if StepStone offers reciprocal affiliate/XML export — not documented in posting guide)
- Endpoint candidates (method + URL):
  - Outbound posting (recruiters): `POST https://recruiter.totaljobs.tjgtest.com/api/v2/job` (test; production URL via Feed Support)
  - Inbound listing ingest: no public jobseeker API found (Reed.co.uk has separate documented jobseeker API — different catalog entry)
- Auth: feed username/password + FEEDID (posting)
- Pagination: N/A for ingest

## Job list / page structure (if known)
- Content-Type: XML for posting payloads
- Path to items / selectors: N/A for consumer ingest
- Key fields observed or documented: StepStone bulk loader fields (title, description, location, apply URL, expiry)

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| — | — | Inbound connector not authorized from posting docs |

## Geo / role fit
- Countries: GB (UK board; StepStone group)
- Fit for FMI Demand Compass: Use Reed jobseeker API (`reed` collector) or Find a Job DWP API for UK public listings instead

## Gaps / next step
- Contact StepStone Feed Support only if pursuing **posting** integration
- For market research ingest, prioritize Reed / DWP / Arbeitnow UK paths; set `NEEDS_CREDENTIALS` only if StepStone confirms export feed

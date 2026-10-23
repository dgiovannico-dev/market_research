# CWJobs (catalog_id=20)

| Field | Value |
|-------|-------|
| Analysis | PARTNER_ONLY |
| Category | A |
| verification_status | UNDER_REVIEW |
| access_mode | unknown |
| connector_key | — |

## Official / docs
- Official: https://www.cwjobs.co.uk/
- Docs / developer: StepStone group — same family as Totaljobs/Jobsite (recruiter XML posting via account manager; no public jobseeker API located)
- Terms / robots notes: UK commercial board; scraping not authorized. Reed jobseeker API covers sibling Reed.co.uk only.

## Access path (for future connector)
- Preferred: partner feed if offered by StepStone sales (not publicly documented)
- Endpoint candidates (method + URL): recruiter XML posting endpoints (outbound only, see Totaljobs StepStone KB)
- Auth: feed credentials from account manager
- Pagination: N/A

## Job list / page structure (if known)
- Content-Type: N/A for inbound ingest
- Path to items / selectors: public HTML search only (not approved)
- Key fields observed or documented: IT/tech focus in UK market

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| — | — | Await StepStone export agreement |

## Geo / role fit
- Countries: GB
- Fit for FMI Demand Compass: Overlap with Reed API, Technojobs RSS, and DWP Find a Job for UK tech roles

## Gaps / next step
- Confirm with StepStone whether any affiliate export exists for CWJobs (distinct from posting API)
- Until then catalog stays UNDER_REVIEW / PARTNER_ONLY — no connector

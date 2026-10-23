# jobs.ch (catalog_id=26)

| Field | Value |
|-------|-------|
| Analysis | PARTNER_ONLY |
| Category | A |
| verification_status | UNDER_REVIEW |
| access_mode | unknown |
| connector_key | — |

## Official / docs
- Official: https://www.jobs.ch/
- Docs / developer: JobCloud affiliate program — https://www.jobcloud.ch/c/de-ch/blog/jobcloud-affiliate-programm-so-werden-sie-partner-von-jobs-ch-jobup-ch-und-jobscout24/
- Terms / robots notes: `robots.txt` disallows `/api/` and `/api_proxy/`; no public developer job search API documented

## Access path (for future connector)
- Preferred: partner XML/JSON feed via JobCloud affiliate
- Endpoint candidates (method + URL):
  - Feed URL issued after approval (contact affiliates@jobcloud.ch)
  - Internal search subdomain `job-search-api.jobs.ch` exists but is not publicly documented for third parties
- Auth: affiliate credentials / signed feed URLs (partner-specific)
- Pagination: defined in feed contract

## Job list / page structure (if known)
- Content-Type: partner XML or JSON feed
- Path to items / selectors: per affiliate integration guide
- Key fields observed or documented: personalization by region, language, employment type (JobCloud blog)

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| stable job UUID | source_job_id | per third-party scraper docs |
| canonical jobs.ch URL | url | |
| title | title | |
| company | company | |
| location / canton | location | CH |
| description | description | |
| workload % | job_type / tags | Swiss Pensum |
| salary | salary_text | when in feed |

## Geo / role fit
- Countries: CH (Switzerland)
- Fit for FMI Demand Compass: CH labor market slice; pair with SECO/BFS stats (category E) for context

## Gaps / next step
- Email affiliates@jobcloud.ch with use-case; request JSON feed for jobs.ch only or combined JobCloud bundle
- Do not call disallowed `/api/` paths without contract

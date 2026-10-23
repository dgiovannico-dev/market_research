# Talent.com (catalog_id=14)

| Field | Value |
|-------|-------|
| Analysis | PARTNER_ONLY |
| Category | A |
| verification_status | UNDER_REVIEW |
| access_mode | unknown |
| connector_key | — |

## Official / docs
- Official: https://www.talent.com/
- Docs / developer: https://employers.talent.com/publishers ; https://www.talent.com/integrations (employer XML ingest)
- Terms / robots notes: Publisher Job API and XML/affiliate programs are contractual; not an anonymous open bulk API. Do not scrape search HTML (aggregator ToS).

## Access path (for future connector)
- Preferred: partner API (publisher backfill) or authorized XML feed
- Endpoint candidates (method + URL):
  - Publisher Job API — contact `publishers@talent.com` / publishers form (self-serve job API for boards; endpoints not public without agreement)
  - Employer-side XML spec documented at talent.com/integrations (inbound to Talent, not job download)
- Auth: publisher credentials / API keys issued by Talent.com
- Pagination: partner-defined (not verified without contract)

## Job list / page structure (if known)
- Content-Type: partner JSON/XML (undocumented publicly)
- Path to items / selectors: N/A without publisher docs
- Key fields observed or documented: publisher materials mention XML job attributes (title, company, location, url, description HTML)

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| partner job id | source_job_id | |
| url / apply link | url | must preserve tracking tokens per contract |
| title | title | |
| company | company | |
| description | description | HTML in XML feed |
| city/region/country | location | |
| date | published_at | |
| salary fields | salary_text | when provided in feed |

## Geo / role fit
- Countries: 79 countries (publisher marketing); global aggregator
- Fit for FMI Demand Compass: Low priority vs free public boards; use only with publisher agreement and clear evidence tier

## Gaps / next step
- Apply via https://employers.talent.com/publishers ; set `NEEDS_CREDENTIALS` after contract
- Prefer existing free paths (Jobicy, Himalayas, Careerjet, Adzuna when keyed) before paid publisher API

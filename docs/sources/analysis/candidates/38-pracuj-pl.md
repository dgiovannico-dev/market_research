# Pracuj.pl (catalog_id=38)

| Field | Value |
|-------|-------|
| Analysis | PARTNER_ONLY |
| Category | A |
| verification_status | UNDER_REVIEW |
| access_mode | unknown |
| connector_key | — |

## Official / docs
- Official: https://www.pracuj.pl/
- Docs / developer: ATS integrations (Workable partner listing); no public jobseeker API on pracuj.pl
- Terms / robots notes: Largest PL job board; scraping prohibited. Employer/aggregator integrations are commercial.

## Access path (for future connector)
- Preferred: partner API / XML feed via Grupa Pracuj commercial agreement
- Endpoint candidates (method + URL): contact Pracuj business integration team (not public)
- Auth: partner credentials
- Pagination: partner-defined

## Job list / page structure (if known)
- Content-Type: N/A publicly
- Path to items / selectors: N/A
- Key fields observed or documented: PL market standard fields (voivodeship, contract, work mode) on website UI

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| offer id | source_job_id | |
| url | url | pracuj.pl offer |
| title | title | |
| employer | company | |
| description | description | |
| location | location | PL |
| salary | salary_text | |
| contract_types | job_type | |

## Geo / role fit
- Countries: PL
- Fit for FMI Demand Compass: High PL coverage potential with partnership; until then use Adzuna PL / authorized aggregators

## Gaps / next step
- Open commercial/API inquiry with Grupa Pracuj
- Cross-check overlap with nofluffjobs (separate collector) for IT subset

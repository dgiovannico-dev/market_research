# DevITJobs (`devitjobs`)

| Field | Value |
|-------|-------|
| Analysis | DONE |
| collection_mode | dump |
| Collector file | `backend/app/collectors/devitjobs.py` |
| Probed_at | 2026-10-21 |
| Sample_records | 365 (live collect, query `python`; 4 hosts) |

## Endpoint

- **Method / URL:** `GET https://devitjobs.{host}/api/jobsLight` per host
- **Hosts:** `uk`, `com`, `nl`, `fr` (config `devitjobs_hosts` overrides order; max 4)
- **Auth:** none; **no server-side query** — full JSON array per host
- **Limits:** `MAX_PER_HOST=120`, `MAX_TOTAL=400`, stratified by `techCategory` (`MAX_PER_CATEGORY=24`)

## Payload / page structure

- **Content-Type:** JSON **array** of job objects
- **Skip:** `isPaused` true, missing `_id` or `jobUrl`
- **Client filter:** `_matches_any` on name, categories, company, technologies, filterTags (OR-split query + optional IT fan-out)
- **Sort/select:** freshest `activeFrom` first, category stratification, dedupe by `_id` and URL

## Field map → RawJob

| Source path | RawJob field | Transform / notes |
|-------------|--------------|-------------------|
| `{host}:{_id}` | source_job_id | composite |
| `jobUrl` slug | url | `https://devitjobs.{host}/jobs/{slug}` |
| `name` | title | |
| `company` | company | |
| _(none)_ | description | `None` |
| cityCategory, actualCity, workplace | location | joined or host TLD upper |
| `activeFrom` | published_at | ISO; invalid logs error, may use now |
| `annualSalaryFrom|To` | salary_text | `{host}`→ GBP/EUR map |
| `techCategory`, `technologies` | tags | category prepended |
| `jobType` | job_type | |
| `workplace`, `remoteType` | remote_hint | remote/full/worldwide→True; office/hybrid→False |
| full item | raw | entire dict stored |

## Gaps / precision risks

- Dump is capped/stratified — not complete market (`dump_complete` false)
- Empty query ingests unfiltered dump up to limits
- `.com` host uses GBP currency mapping (code convention)
- Multi-host errors collected per TLD without failing whole run

## Live sample (redacted)

```json
{
  "_id": "6ad8abf2…",
  "name": "Lead Full-Stack Software Engineer",
  "company": "TPXImpact Holdings Plc",
  "jobUrl": "TPXImpact-Holdings-Plc-Lead-Full-Stack-…",
  "activeFrom": "2026-10-21T12:11:30.820000+00:00",
  "annualSalaryFrom": 85000,
  "annualSalaryTo": 85000,
  "workplace": "remote",
  "techCategory": "DevOps",
  "technologies": ["AI", "AWS", "Azure"]
}
```

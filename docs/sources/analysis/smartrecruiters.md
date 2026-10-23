# SmartRecruiters API (`smartrecruiters`)

| Field | Value |
|-------|-------|
| Analysis | DONE |
| collection_mode | dump |
| Collector file | `backend/app/collectors/smartrecruiters.py` |
| Probed_at | 2026-10-21 |
| Sample_records | up to 200/company (2 pages × limit 100); probe tenant e.g. `endava` |

## Endpoint

- **Method / URL template:** `GET https://api.smartrecruiters.com/v1/companies/{company}/postings`
- **Auth:** none (public company postings)
- **Env tenant list:** `SMARTRECRUITERS_COMPANIES` (CSV; see `docs/sources/ATS_TENANTS.md`)
- **Query:** `limit=100`, `offset=<n>`
- **Pagination / caps:** max **2 pages** per company; stop when `content` empty, `offset >= totalFound`, or short page
- **Note:** no `MAX_PER_TENANT` — page cap only

## Payload / page structure

- **Content-Type:** `application/json`
- **Path to jobs:** `content[]`
- **Meta:** `totalFound`
- **Per-item keys used:** `id`, `name`, `postingUrl`, `company.identifier`, `location.fullLocation|city|remote|hybrid`, `releasedDate`, `defaultJobAd`/`jobAd.sections.*.text`, `department.label`, `function.label`, `experienceLevel.id`

## Field map → RawJob

| Source path | RawJob field | Transform / notes |
|-------------|--------------|-------------------|
| `{ident}:{id}` | source_job_id | `ident` = `company.identifier` or tenant slug |
| `postingUrl` else constructed jobs.smartrecruiters.com URL | url | slug from title |
| `name` | title | fallback Untitled |
| `ident` | company | company identifier token |
| `defaultJobAd`/`jobAd` sections text joined | description | **often null** when `defaultJobAd` is boolean `true` (no sections in list) |
| `location.fullLocation` else `city` | location | |
| `releasedDate` ISO | published_at | else now UTC |
| department / function / experienceLevel | tags | labels only |
| `location.remote` / `hybrid` | remote_hint | True / None / False |

## Gaps / precision risks

- List payloads frequently omit full job ad → **description null** (thin skill extraction)
- Company = SmartRecruiters identifier, not legal name
- 2×100 cap under-samples large companies

## Live sample (redacted)

```json
{
  "id": "a1b2c3",
  "name": "Software Engineer",
  "postingUrl": "https://jobs.smartrecruiters.com/Endava/a1b2c3-software-engineer",
  "company": { "identifier": "Endava" },
  "location": { "city": "London", "fullLocation": "London, UK", "remote": false },
  "releasedDate": "2026-10-15T00:00:00.000Z",
  "defaultJobAd": true,
  "department": { "label": "Engineering" }
}
```

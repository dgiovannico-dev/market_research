# Workday Careers CXS (`workday`)

| Field | Value |
|-------|-------|
| Analysis | DONE |
| collection_mode | dump |
| Collector file | `backend/app/collectors/workday.py` |
| Probed_at | 2026-10-21 (15 default tenants) |
| Sample_records | max 40/tenant (`MAX_PER_TENANT`); page `limit=20` |

## Endpoint

- **Method / URL template:** `POST https://{tenant}.{wd}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs`
- **Body:** `{"appliedFacets":{},"limit":20,"offset":0,"searchText":""}`
- **Auth:** none on public external career sites
- **Env tenant list:** `WORKDAY_TENANTS` — CSV of `tenant:wdN:siteSlug` (see `docs/sources/ATS_TENANTS.md`)
- **Pagination:** increase `offset` until `offset >= total` or 40 matched jobs
- **Not used:** HTML career pages; internal/unlisted Workday sites

## Payload / page structure

- **Content-Type:** `application/json`
- **Path:** `jobPostings[]`; `total`
- **Per-item keys used:** `title`, `externalPath`, `locationsText`, `postedOn`, `bulletFields`

## Field map → RawJob

| Source path | RawJob field | Transform / notes |
|-------------|--------------|-------------------|
| `{tenant}:{bulletFields[0]}` else path slug | source_job_id | |
| `https://{tenant}.{wd}.myworkdayjobs.com/{site}{externalPath}` | url | |
| `title` | title | |
| tenant token (title-cased) | company | not always legal employer name |
| — | description | listing has no body; detail CXS optional later |
| `locationsText` | location | free text |
| `postedOn` | published_at | relative text → collect time (UTC now) |

## Gaps / precision risks

- Wrong `wd` shard or `site` slug → **422**; probe before adding
- Some tenants return **401** for guessed sites (not public)
- `postedOn` is relative (“Posted Today”) — not a durable ISO timestamp
- Detail description requires a second CXS GET (not fetched in v1)

## Live sample (redacted)

```json
{
  "title": "Senior Software Development Engineer, Neural Graph Infrastructure",
  "externalPath": "/job/US-CA-Santa-Clara/Senior-CAD-Infrastructure-Development-Engineer_JR2010334",
  "locationsText": "US, CA, Santa Clara",
  "postedOn": "Posted Today",
  "bulletFields": ["JR2010334"]
}
```

# Teamtailor career JSON Feed (`teamtailor`)

| Field | Value |
|-------|-------|
| Analysis | DONE |
| collection_mode | dump |
| Collector file | `backend/app/collectors/teamtailor.py` |
| Probed_at | 2026-10-21 |
| Sample_records | max 40/host (`MAX_PER_TENANT`); up to 3 pages via `next_url` |

## Endpoint

- **Method / URL template:** `GET https://{host}/jobs.json`
- **Auth:** none (public JSON Feed where enabled)
- **Env tenant list:** `TEAMTAILOR_HOSTS` (CSV hosts; subdomain or custom domain — see `docs/sources/ATS_TENANTS.md`)
- **Pagination:** follow `next_url` up to **3** pages / host; ingest stops at **40** matched jobs
- **Not used:** `api.teamtailor.com` JSON:API (tenant API key; PARTNER_ONLY for cross-tenant)

## Payload / page structure

- **Content-Type:** `application/json` (JSON Feed 1.1)
- **Path:** `items[]`; optional feed `title`, `home_page_url`, `next_url`
- **Per-item keys used:** `id`, `title`, `url`, `date_published`, `content_html`, `_jobposting` (schema.org JobPosting)

## Field map → RawJob

| Source path | RawJob field | Transform / notes |
|-------------|--------------|-------------------|
| `{host}:{_jobposting.identifier.value}` else `{host}:{id}` | source_job_id | |
| `url` | url | |
| `title` | title | |
| `_jobposting.hiringOrganization.name` else feed `title` | company | |
| `content_html` else `_jobposting.description` | description | HTML kept |
| `_jobposting.jobLocation[].address` | location | locality, region, country |
| `date_published` | published_at | ISO-8601 |

## Gaps / precision risks

- Some career sites disable `/jobs.json` (404) — probe before adding hosts
- Remote flag rarely present in feed
- Custom domains common; store host as configured, not assumed `*.teamtailor.com`

## Live sample (redacted)

```json
{
  "id": "a775edab-…",
  "title": "Head of Customer Engagement Benelux",
  "url": "https://polestar.teamtailor.com/jobs/8551558-…",
  "date_published": "2026-10-15T13:14:55+02:00",
  "_jobposting": {
    "identifier": {"value": 8551558},
    "hiringOrganization": {"name": "Polestar"},
    "jobLocation": [{"address": {"addressLocality": "Beesd", "addressCountry": "NL"}}]
  }
}
```

# Reed (`reed`)

| Field | Value |
|-------|-------|
| Analysis | DONE |
| collection_mode | feed (RSS default); search via API when `REED_API_KEY` set |
| Collector file | `backend/app/collectors/reed.py` |
| Probed_at | 2026-10-21 |
| Sample_records | 25 (RSS, no query) |

## Endpoint

- **RSS (default):** `GET https://www.reed.co.uk/jobs/rss` — optional `keywords` query param.
- **JSON API (credentialed):** `GET https://www.reed.co.uk/api/1.0/search` — Basic auth `(REED_API_KEY, "")`, params `keywords`, `resultsToTake=50`, `resultsToSkip=0`. Blank query → `missing_query`.
- **Pagination:** single page (50 API / full RSS channel).

## Payload / page structure

- **RSS:** XML `channel/item` with `title`, `link`, `guid`, `description`, optional Atom `updated`.
- **API:** JSON `{ "results": [ { jobId, jobTitle, jobUrl, employerName, jobDescription, locationName, county, country, date, minimumSalary, maximumSalary, currency, contractType, ... } ] }`.

## Field map → RawJob

| RawJob | RSS path | API path |
|--------|----------|----------|
| `source_job_id` | `guid` or link/title | `jobId` |
| `url` | `link` (http→https) | `jobUrl` |
| `title` | `title` | `jobTitle` |
| `company` | `None` | `employerName` |
| `description` | HTML-stripped `description` | `jobDescription` |
| `location` | constant `"UK"` | join `locationName`, `county`, `country` |
| `published_at` | `updated` element or UTC now | `date` ISO or UTC now |
| `salary_text` | regex from description | `min-max currency` from salary fields |
| `tags` | `[]` | `[]` |
| `job_type` | `None` | `contractType` |
| `remote_hint` | `None` | `None` |
| `raw` | `{title, link, mode: rss}` | full item + `mode: api` |

## Gaps / precision risks

- RSS omits employer; location always `UK` (not parsed from text).
- API path requires key + query; not used in default feed crawl.
- RSS salary is heuristic regex on HTML blurb only.

## Live sample (redacted)

```json
{
  "source_job_id": "57480647",
  "title": "FPGA Engineer - London or Amsterdam- Leading High Frequency …",
  "url": "https://www.reed.co.uk/jobs/fpga-engineer-london-or-amsterdam-…",
  "company": null,
  "location": "UK",
  "mode": "rss"
}
```

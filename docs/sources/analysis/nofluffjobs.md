# NoFluffJobs (`nofluffjobs`)

| Field | Value |
|-------|-------|
| Analysis | DONE |
| collection_mode | dump |
| Collector file | `backend/app/collectors/nofluffjobs.py` |
| Probed_at | 2026-10-21 |
| Sample_records | 100 (`query=python`, `MAX_RECORDS`) |

## Endpoint

- **URL:** `GET https://nofluffjobs.com/api/posting`
- **Body:** JSON `{ "postings": [ ... ] }` (large public dump).
- Client filter on query substring; cap 100 matches.

## Payload / page structure

- Posting: `id`, `url` (slug), `title`, `name` (company), `category`, `posted`/`renewed` (epoch ms), `location`, `salary`, `tiles`, `seniority`, `fullyRemote`.

## Field map → RawJob

| RawJob | Source |
|--------|--------|
| `source_job_id` | `id` |
| `url` | `https://nofluffjobs.com/pl/job/{url slug}` |
| `title` | `title` |
| `company` | `name` |
| `description` | `None` (not in dump) |
| `location` | `location.places[0]` city + country code; remote type |
| `published_at` | `posted` or `renewed` ms → UTC |
| `salary_text` | `salary.from-to currency/period (type)` |
| `tags` | category, requirement tiles, seniority |
| `job_type` | `salary.type` (contract) |
| `remote_hint` | `fullyRemote` or `location.type` |
| `raw` | full posting minus `logo` |

## Gaps / precision risks

- No job body in public dump; evidence is list metadata only.
- Scan order-dependent when filtering; may miss matches beyond first 100 hits.
- URL hardcoded `/pl/job/` locale.

## Live sample (redacted)

```json
{
  "source_job_id": "…",
  "title": "Data Engineer – Recovery Data Management",
  "company": "DCG",
  "description": null,
  "location": "Warsaw, PL"
}
```

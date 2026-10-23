# Lever Postings (`lever`)

| Field | Value |
|-------|-------|
| Analysis | DONE |
| collection_mode | dump |
| Collector file | `backend/app/collectors/ats_boards.py` |
| Probed_at | 2026-10-21 |
| Sample_records | 40 max/tenant (`MAX_PER_TENANT`; probe `spotify` lists 78 postings) |

## Endpoint

- **Method / URL template:** `GET https://api.lever.co/v0/postings/{site}?mode=json`
- **Auth:** none (public postings)
- **Env tenant list var:** `LEVER_SITES` (comma-separated site slugs; see `docs/sources/ATS_TENANTS.md`)
- **Pagination / MAX_PER_TENANT:** one JSON array per site; ingest stops at **40 jobs per site** after optional query filter

## Payload / page structure

- **Content-Type:** `application/json`
- **Path to jobs array:** top-level JSON **array** (not wrapped)
- **Per-item keys (read by collector):** `id`, `text`, `hostedUrl`, `applyUrl`, `createdAt`, `categories.location`, `categories.commitment`, `categories.team`, `descriptionPlain`, `description`

## Field map → RawJob

| Source path | RawJob field | Transform / notes |
|-------------|--------------|-------------------|
| `id` + site slug | source_job_id | `f"{site}:{id}"` |
| `hostedUrl` or `applyUrl` | url | first non-empty |
| `text` | title | fallback `"Untitled"` |
| site slug (env) | company | |
| `descriptionPlain` or `description` | description | string only; HTML possible on `description` |
| `categories.location` | location | |
| `createdAt` | published_at | ms epoch → UTC; on failure → now UTC |
| `categories.commitment`, `categories.team` | tags | non-empty values only, order preserved |
| _(literal)_ | remote_hint | not set |
| subset | raw | `{"id", "text", "site"}` |

Optional **query:** substring on `text` (title) only.

## Gaps / precision risks

- **40-job cap** per site; order is API default (often createdAt desc) — not full board.
- Site slug may 404 when companies rebrand or leave Lever (see ATS tenant doc).
- `description` may be HTML when `descriptionPlain` absent.
- Workplace / country not mapped; no `remote_hint`.

## Live sample (redacted)

```json
{
  "id": "00000000-0000-0000-0000-000000000000",
  "text": "Backend Engineer",
  "hostedUrl": "https://jobs.lever.co/spotify/…",
  "createdAt": 1720000000000,
  "categories": {
    "location": "Stockholm",
    "commitment": "Full-time",
    "team": "Engineering"
  },
  "descriptionPlain": "We are looking for…"
}
```

# Greenhouse Job Boards (`greenhouse`)

| Field | Value |
|-------|-------|
| Analysis | DONE |
| collection_mode | dump |
| Collector file | `backend/app/collectors/ats_boards.py` |
| Probed_at | 2026-10-21 |
| Sample_records | 40 max/tenant (`MAX_PER_TENANT`; probe `airbnb` board lists 186 jobs) |

## Endpoint

- **Method / URL template:** `GET https://boards-api.greenhouse.io/v1/boards/{board}/jobs`
- **Auth:** none (public boards)
- **Env tenant list var:** `GREENHOUSE_BOARDS` (comma-separated board tokens; see `docs/sources/ATS_TENANTS.md`)
- **Pagination / MAX_PER_TENANT:** single response per board (no pagination); ingest stops at **40 jobs per board** after optional query filter; listing omits `content=true` (no per-job body fetch)

## Payload / page structure

- **Content-Type:** `application/json`
- **Path to jobs array:** `jobs[]`
- **Per-item keys (read by collector):** `id`, `title`, `absolute_url`, `location.name`, `updated_at`, `created_at` (also present on live boards: `company_name`, `metadata`, etc., unused)

## Field map → RawJob

| Source path | RawJob field | Transform / notes |
|-------------|--------------|-------------------|
| `id` + board slug | source_job_id | `f"{board}:{id}"` |
| `absolute_url` | url | empty string if missing |
| `title` | title | fallback `"Untitled"` |
| board token (env) | company | **not** API `company_name` |
| _(literal)_ | description | always `None` (listing only; no description fetch) |
| `location.name` | location | via `(location or {}).get("name")` |
| `updated_at` or `created_at` | published_at | ISO parse (`Z`→`+00:00`); on failure or missing → now UTC |
| _(literal)_ | remote_hint | always `None` |
| _(literal)_ | tags | default empty (not set) |
| subset | raw | `{"id", "title", "board"}` only |

Optional **query:** case-insensitive substring match on `title` only; API order preserved until cap.

## Gaps / precision risks

- **Description omitted** by design; skills/text not in listing payload.
- **Company** is board token, not employer display name from JSON.
- First 40 title-matching jobs only — large boards are sampled, not complete (`dump_complete` stays false).
- Query ignores location, metadata (e.g. Workplace Type), and body text.

## Live sample (redacted)

```json
{
  "id": 7789554,
  "title": "Associate Legal Counsel, Japan",
  "absolute_url": "https://careers.airbnb.com/positions/7789554?gh_jid=7789554",
  "location": { "name": "Tokyo, Japan" },
  "updated_at": "2026-09-29T20:00:54-04:00",
  "company_name": "Airbnb"
}
```

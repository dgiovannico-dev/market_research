# ViewJobs (`viewjobs`)

| Field | Value |
|-------|-------|
| Analysis | DONE |
| collection_mode | search |
| Collector file | `backend/app/collectors/viewjobs.py` |
| Probed_at | 2026-10-21 |
| Sample_records | 39 |

## Endpoint
- Method / URL: POST `https://www.viewjobs.com.au/api/mcp` (JSON-RPC `tools/call`)
- Auth: None; agent docs `https://www.viewjobs.com.au/for-agents`
- Query / body params: `search_jobs` with `query` + `place` (6 AU metros); blank query → `missing_query`
- Pagination: Fan-out 6 places × 1 query; max 120 unique jobs
- Rate limit / ToS notes: UTM/attribution on URLs; thin evidence tier in raw

## Payload / page structure
- Content-Type: `application/json` or SSE (`data: {json}`)
- Path to job list: `result.structuredContent.jobs[]`
- Per-item keys (from tests + MCP): `id`, `title`, `employer`, `location`, `work_type`, `apply_type`, `pay`, `posted_at`, `url`, `featured`
- Nested paths that matter: SSE wrapper parsing via `_parse_sse_payload`

## Field map → RawJob
| Source path | RawJob field | Transform / notes |
|-------------|--------------|-------------------|
| `id` | source_job_id | dedupe across places |
| `url` | url | strip query string |
| `title` | title | |
| `employer` | company | |
| — | description | always `None` |
| `location` | location | append `, Australia` if missing |
| `posted_at` | published_at | ISO8601 |
| `pay` | salary_text | |
| work_type, apply_type | tags | max 8 |
| `work_type` | job_type | |
| — | remote_hint | `None` |

## Gaps / precision risks
- No job body/description in MCP payload
- 6-city fan-out may miss regional listings
- Per-place errors collected but partial results OK
- Search-mode requires explicit query (ADR-007)

## Live sample (redacted)
```json
{"id": "abc-123", "title": "Python Developer", "employer": "Tech Co", "location": "Sydney, NSW", "work_type": "full-time", "posted_at": "2026-10-14T23:49:35.833Z", "url": "https://www.viewjobs.com.au/listing/abc-123"}
```

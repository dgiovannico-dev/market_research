# HN Who is hiring (`hn_whoishiring`)

| Field | Value |
|-------|-------|
| Analysis | DONE |
| collection_mode | feed |
| Collector file | `backend/app/collectors/hn_whoishiring.py` |
| Probed_at | 2026-10-21 |
| Sample_records | 178 |

## Endpoint
- Method / URL: GET `https://hn.algolia.com/api/v1/search_by_date`
- Auth: None (Algolia public HN index)
- Query / body params: (1) `tags=story,author_whoishiring`, `hitsPerPage=1` → latest thread; (2) `tags=comment,story_{id}`, `hitsPerPage=100`, `page=0..2`
- Pagination: Up to 3 comment pages × 100 hits
- Rate limit / ToS notes: Not HTML scrape; heuristic hiring-comment filter

## Payload / page structure
- Content-Type: `application/json`
- Path to job list: `hits[]` on comment search (story in first call)
- Per-item keys (Algolia comment hit): `_highlightResult`, `_tags`, `author`, `children`, `comment_text`, `created_at`, `created_at_i`, `objectID`, `parent_id`, `story_id`, `story_title`, `updated_at`
- Nested paths that matter: plain text from `comment_text` (HTML stripped)

## Field map → RawJob
| Source path | RawJob field | Transform / notes |
|-------------|--------------|-------------------|
| `objectID` | source_job_id | comment id |
| constructed | url | `https://news.ycombinator.com/item?id={objectID}` |
| parsed first line | title | pipe-delimited heuristic |
| parsed first segment | company | |
| `comment_text` | description | plain, max 8000 chars |
| text contains "remote" | location | `"Remote"` if true else `None` |
| `created_at` | published_at | ISO8601 |
| story title | tags | one tag, truncated 80 |
| — | salary_text | not extracted |
| — | job_type | not mapped |
| "remote" in text | remote_hint | bool or None |

## Gaps / precision risks
- One hiring thread per month; stale until new story
- Heuristic drops “seeking work” and non-hiring comments
- `raw` omits full Algolia hit (only story_id, author)
- Title/company parsing brittle without `|` format

## Live sample (redacted)
```json
{"objectID": "12345678", "author": "kscan1992", "comment_text": "Acme | Senior Python Engineer | Remote | …truncated ~200 chars", "created_at": "2026-10-01T12:00:00Z", "story_id": 49922569}
```

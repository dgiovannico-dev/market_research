# We Work Remotely (`weworkremotely`)

| Field | Value |
|-------|-------|
| Analysis | DONE |
| collection_mode | feed |
| Collector file | `backend/app/collectors/weworkremotely.py` |
| Probed_at | 2026-10-21 |
| Sample_records | 25 |

## Endpoint
- Method / URL: GET `https://weworkremotely.com/categories/remote-programming-jobs.rss`
- Auth: None
- Query / body params: none; client-side filter on title/description
- Pagination: RSS single channel (~25 items in probe)
- Rate limit / ToS notes: RSS polling; programming category only

## Payload / page structure
- Content-Type: `application/rss+xml` (parsed as XML)
- Path to job list: `/rss/channel/item[]` (ElementTree `./channel/item`)
- Per-item keys (RSS elements used): `title`, `link`, `description`, `pubDate`, `guid`
- Nested paths that matter: title often `"Company: Role"`

## Field map → RawJob
| Source path | RawJob field | Transform / notes |
|-------------|--------------|-------------------|
| `guid` / `link` / `title` | source_job_id | |
| `link` | url | |
| `title` | title | split on first `:` → company + role |
| (from title split) | company | |
| `description` | description | strip HTML tags via regex |
| — | location | constant `"Remote"` |
| `pubDate` | published_at | RFC822 → datetime |
| — | salary_text | not in feed |
| — | tags | empty |
| — | job_type | not mapped |
| — | remote_hint | always `True` |

## Gaps / precision risks
- `raw` stores only `{title, link}` — full RSS item discarded
- Company parsing fails if title lacks `:`
- Single category feed; not full site
- Description is often short RSS snippet

## Live sample (redacted)
```xml
<item><title>Stripe: Abuse Research Engineer</title><link>https://weworkremotely.com/remote-jobs/stripe-abuse-research-engineer</link><description>…truncated…</description></item>
```

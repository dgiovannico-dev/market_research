# NAV Stillingsfeed (`nav_stilling_feed`)

| Field | Value |
|-------|-------|
| Analysis | DONE |
| collection_mode | dump |
| Collector file | `backend/app/collectors/nav_stilling_feed.py` |
| Probed_at | 2026-10-21 |
| Sample_records | ≤100 ACTIVE in 7-day `If-Modified-Since` window (3 pages max) |

## Endpoint

- **Token:** `GET https://pam-stilling-feed.nav.no/api/publicToken` → extract JWT from plain text
- **Feed:** `GET https://pam-stilling-feed.nav.no/api/v1/feed` with `Authorization: Bearer` + `If-Modified-Since` (GMT); follow relative `next_url`
- **Tip:** `?last=true` returns the newest page (often 1 item)
- Blank query OK (dump). Optional client substring on title/employer/municipal.
- `dump_complete=false` (windowed + capped).

## Payload / page structure

- JSON Feed-style page: `items[]` with `_feed_entry.{uuid,status,title,businessName,municipal,sistEndret}`
- Default feed start is historical INACTIVE; IMS / `last` required for recent ACTIVE
- Feedentry detail (`ad_content`) not fetched in thin collector

## Field map → RawJob

| RawJob | Source |
|--------|--------|
| `source_job_id` | `_feed_entry.uuid` |
| `url` | arbeidsplassen stilling URL |
| `title` | `_feed_entry.title` |
| `company` | `businessName` |
| `description` | `None` (thin; no N+1) |
| `location` | `"{municipal}, Norway"` |
| `published_at` | `date_modified` |

## Dedupe vs `nav_arbeidsplassen`

Same UUID + stilling URL → `canonical_url` merge. Search is query mode; this is time-window dump.

## Gaps / precision risks

- Public token rotates; private consumer token recommended for production
- No description/tags/remote without feedentry enrichment
- Incorrect IMS weekday → server ignores header and returns historical start

# Technojobs (catalog_id=21)

| Field | Value |
|-------|-------|
| Analysis | DOCUMENTED — **blocked on probe** |
| Category | A |
| verification_status | UNDER_REVIEW |
| access_mode | unknown |
| connector_key | — |
| Probed_at | 2026-10-21 |

## Official / docs
- Official: https://www.technojobs.co.uk/
- Docs / developer: https://www.technojobs.co.uk/rss-about.phtml (RSS feed documentation)
- Terms / robots notes: Public RSS tied to saved search parameters; employer posting uses partner XML (eQuest/Workable) — separate outbound path

## Access path (for future connector)
- Preferred: RSS/Atom per search URL
- Endpoint candidates (method + URL):
  - `GET https://www.technojobs.co.uk/rss.php/{search terms}/excludekeywords/{locations}/radius{mi}/termsin0/salary0/postedwithinall/jobtypeall/searchfieldRSearchIndex/page1`
  - Build RSS URL from on-site search results “subscribe to RSS” link for each intent
- Auth: none for RSS
- Pagination: RSS pages via `pageN` segment; poll per saved query

## Job list / page structure (if known)
- Content-Type: RSS/XML
- Path to items / selectors: standard RSS `<item>` entries (title, link, description, pubDate)
- Key fields observed or documented: search dimensions encoded in URL path (keywords, geo, radius, job type)

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| guid or link | source_job_id | hash link if no id |
| link | url | |
| title | title | |
| description | description | often snippet |
| pubDate | published_at | RSS date |
| — | company | parse from description if present |
| — | location | from search context / item text |
| tags | tags | IT focus |

## Geo / role fit
- Countries: GB, IE (search locations include Ireland, Scotland, Wales, England)
- Fit for FMI Demand Compass: Strong for UK/Ireland IT contractor/permanent signals via RSS search intents

## Gaps / next step
- **2026-10-21 probe:** `rss-about.phtml` and sample `rss.php/…` URLs return HTML lander (`window.location.href="/lander"`), not RSS — bot/geo wall. No connector until a stable feed is confirmed (browser cookie path = not ADR-003-safe).
- Prefer Reed free RSS / Adzuna UK key / other ACTIVE UK ATS for Demand Compass UK signal.
- Re-probe periodically; if RSS returns `application/rss+xml` again, implement feed collector with IT keyword set.

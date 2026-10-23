# Recruitee (catalog_id=94)

| Field | Value |
|-------|-------|
| Analysis | IMPLEMENTED |
| Category | D |
| verification_status | ACTIVE |
| access_mode | public_api_per_company |
| connector_key | `recruitee` |
| Collector sheet | [../recruitee.md](../recruitee.md) |

## Official / docs
- Official: https://recruitee.com/
- Docs / developer: https://docs.recruitee.com/reference/intro-to-careers-site-api — Careers Site API (public offers collection).
- Terms / robots notes: Public careers endpoints on employer subdomain or custom domain; ATS API (`api.recruitee.com`) requires token and is not a substitute for cross-company ingest.

## Access path (for future connector)
- Preferred: public Careers Site JSON (and optional XML feed) on employer host.
- Endpoint candidates (method + URL):
  - `GET https://{slug}.recruitee.com/api/offers/` — published jobs JSON (docs: replace subdomain; works on custom domain as `/api/offers/` on careers host).
  - `GET https://{slug}.recruitee.com/api/offers.xml` or `/api/feeds/offers.xml` — XML alternative.
- Auth: none for careers site offers.
- Pagination: typically single response per company (verify large boards); filter query params `department`, `tag` per docs.

## Job list / page structure (if known)
- Content-Type: `application/json`
- Path to items: `offers[]` (response wrapper; field order varies).
- Key fields documented: `id`, `slug`, `title`, `description`, `location`, `department`, `tags`, `careers_url`, `published_at`, `remote`, `country`, `city`.

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| `id` | source_job_id | slug-prefix `{host}:{id}` |
| `careers_url` or built from slug | url | |
| `title` | title | |
| company name in offer or host | company | |
| `description` | description | HTML/plain per offer |
| `city` / `country` / `location` | location | compose |
| `published_at` | published_at | |
| `remote` | remote_hint | when present |

## Geo / role fit
- Countries: EU-heavy; Tellent Recruitee customers globally.
- Fit for FMI Demand Compass: strong for curated slug list (`RECRUITEE_SLUGS` or career URLs); complements IT/CH/DE employer boards.

## Gaps / next step
- Probe real slug list; empty `offers[]` still valid (200).
- Confirm custom-domain discovery from catalog metadata.
- ATS token path = PARTNER_ONLY per employer, not bulk market index.
- **Deadline:** Recruitee docs set **2027-02-10** as end of unauthenticated Careers Site API — after that require `X-Careers-Sites-Token`. Build connector now while keyless; plan token env later.

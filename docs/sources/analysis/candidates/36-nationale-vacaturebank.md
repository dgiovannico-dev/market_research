# Nationale Vacaturebank (catalog_id=36)

| Field | Value |
|-------|-------|
| Analysis | PARTNER_ONLY |
| Category | A |
| verification_status | UNDER_REVIEW |
| access_mode | partner_or_unknown |
| connector_key | — |

## Official / docs
- Official: https://www.nationalevacaturebank.nl/
- **Employer posting API (documented):** Teamtailor integration — API key from **DPG Media Employment Solutions** dashboard → Job Poster → API key; activate in ATS marketplace https://support.teamtailor.com/en/articles/17172426-publish-jobs-on-nationale-vacaturebank (posting/sync only, not third-party job search)
- Employer terms hub: https://www.nationalevacaturebank.nl/werkgever/algemene-voorwaarden (DPG Media AV, Feb 2025 PDF download)
- **No official public jobseeker/search API** in DPG docs Oct 2026; community clients cite `https://api.nationalevacaturebank.nl` — probe `GET .../jobs?limit=1` returned **404** (Oct 2026)
- Lawful NL alternative in repo: **findmethatdamjob** / Adzuna NL per catalog notes
- Terms / robots notes: Do not treat StackOverflow `zoeken.json` or unofficial SDKs as authorized ingest ([ADR-003](../../decisions/ADR-003-authorized-connectors-only.md))

## Access path (for future connector)
- Preferred: DPG-confirmed **research/syndication** API or licensed feed; else findmethatdamjob
- Endpoint candidates (method + URL):
  - Employer outbound: DPG dashboard API key (Teamtailor docs)
  - Search: none verified official Oct 2026
- Auth: employer API key for posting; search auth unknown
- Pagination: n/a until official search product

## Job list / page structure (if known)
- Content-Type: HTML/SPA on site; alleged JSON on unofficial hosts — unverified
- Third-party typings (unofficial): title, company, salary, contractType — not used without DPG contract

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| id | source_job_id | after authorized schema |
| vacancy URL | url | nationalevacaturebank.nl |
| title | title | |
| company | company | |
| description | description | |
| city | location | NL |

## Geo / role fit
- Countries: NL
- Fit for FMI Demand Compass: Prefer **findmethatdamjob** collector; NVB only after DPG research API terms

## Gaps / next step
- Contact customerservice@nationalevacaturebank.nl / DPG for **jobseeker/research** API (distinct from posting key)
- Until partnership: no ACTIVE NVB connector; no scrape of zoeken.json

# Guru (catalog_id=49)

| Field | Value |
|-------|-------|
| Analysis | BLOCKED_TOS |
| Category | B |
| verification_status | UNDER_REVIEW |
| access_mode | unknown |
| connector_key | — |

## Official / docs
- Official: https://www.guru.com/ (freelance marketplace).
- Docs / developer: **No public job-board API.** `developer.getguru.com` / `api.getguru.com` is **Guru (knowledge management)** — unrelated product; do not conflate.
- Terms / robots notes: Open jobs are HTML category listings (`/d/jobs/c/...`); no RSS/JSON job index published. Third-party scrapers exist but are not authorized for FMI (ADR-003).

## Access path (for future connector)
- Preferred: none suitable — partner/data license if Guru offers employer integrations (not verified publicly).
- Endpoint candidates (method + URL): none for marketplace job search.
- Auth: N/A for listings.
- Pagination: N/A.

## Job list / page structure (if known)
- Content-Type: server-rendered HTML on public browse pages.
- WorkRoom APIs are post-hire workspace features, not open job discovery ([Guru Help: WorkRoom](https://www.guru.com/help/freelancer/workroom-freelancer/)).
- Key fields visible on listings: title, budget type/range, skills, employer country, quotes — web UI only.

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| — | — | No authorized mapping |

## Geo / role fit
- Countries: global; US-heavy employer base.
- Fit for FMI Demand Compass: **Low** until lawful feed; overlap with Freelancer.com API and other gig boards.

## Gaps / next step
- Contact Guru business development for syndication/API if available; do not implement HTML harvest.
- Deprioritize vs `45-freelancer.md` (DOCUMENTED REST path).

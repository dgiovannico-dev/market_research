# freelancermap (catalog_id=52)

| Field | Value |
|-------|-------|
| Analysis | PARTNER_ONLY |
| Category | B |
| verification_status | NEEDS_CREDENTIALS |
| access_mode | partner_or_unknown |
| connector_key | — |

## Official / docs
- Official: https://www.freelancermap.com/ (DE: https://www.freelancermap.de/projekte)
- **Automated project import (documented, employer → platform):** FAQ https://www.freelancermap.com/help.html — Enterprise members push projects via **XML or JSON**; integrations (Broadbean, LogicMelon); contact **support@freelancermap.com**; brochure https://www.freelancermap.com/images/brochure/Automated-project-import-freelancermap.pdf (required XML fields: `external_id`, `proj_title`, `proj_type`, `proj_duration`, `proj_country`, `proj_city`, `proj_description`, `start_month`, `start_year`; feed **pulled** by freelancermap ~every 3h)
- **No official public “projects export” API** for jobseekers/researchers on help/pricing pages — import docs are **inbound** to freelancermap only
- Legacy RSS URLs (e.g. `.../feeds/projects/int-international.xml`) cited in community lists; probes Oct 2026 returned **404/403** — not treated as authorized connector without publisher confirmation
- Third-party paid wrappers (e.g. everydata.io `/fmp/...`) are **not** authorized sources ([ADR-003](../../decisions/ADR-003-authorized-connectors-only.md))

## Access path (for future connector)
- Preferred: **negotiated read/syndication feed or data license** from Verlag J. Maiss / freelancermap (mirror employer XML schema or API export if offered)
- Endpoint candidates (method + URL):
  - Contractual XML/JSON URL (employer import schema as reference for field names only)
  - Public website search HTML — **not** authorized for scraping
- Auth: enterprise account / contractual token if read feed exists
- Pagination: unknown for any read API; import feeds are employer-controlled

## Job list / page structure (if known)
- Content-Type: XML (employer import); public site is HTML search
- Import fields map to IT contract projects: title, type (Remote|Contract|Permanent), duration (months), country/city, description, start date

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| external_id / projectId | source_job_id | |
| project URL | url | freelancermap.de/.com projekt path |
| proj_title | title | |
| publisher company name | company | from listing when shown |
| proj_description | description | |
| proj_country, proj_city, remote % | location / remote_hint | |
| start_month/year, duration | job_type / metadata | contract vs permanent |

## Geo / role fit
- Countries: DE/DACH + international IT freelance
- Fit for FMI Demand Compass: **Medium** for DACH IT contract demand **if** licensed read feed or partnership confirmed

## Gaps / next step
- Email support@freelancermap.com asking for **researcher/syndication read API** (distinct from employer import)
- Until partnership: no ACTIVE connector; do not scrape search results or use third-party scraper APIs

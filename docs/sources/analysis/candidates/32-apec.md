# APEC (catalog_id=32)

| Field | Value |
|-------|-------|
| Analysis | PARTNER_ONLY |
| Category | A |
| verification_status | UNDER_REVIEW |
| access_mode | unknown |
| connector_key | — |

## Official / docs
- Official: https://www.apec.fr/
- Docs / developer: Recruiter ATS API ADEP (2026); XML export partnership — https://www.apec.fr/faq.html?question=comment-puis-je-publier-des-offres-d-emploi-en-utilisant-un-flux-xml
- Terms / robots notes: Documented automation is **recruiter → APEC** (publish offers). Bulk **export** of cadre listings requires partnership form (“Devenir partenaire”). No open bulk consumer API verified.

## Access path (for future connector)
- Preferred: partner XML export or approved API (after APEC partnership review)
- Endpoint candidates (method + URL):
  - ADEP ATS multidiffusion (employer-side): recruiter credentials + numéro interlocuteur
  - Export flux XML standardisé: via partnership request (fields TBD by APEC)
  - Public candidate app endpoints (e.g. offer detail) exist for logged-in UX — not licensed for bulk harvest
- Auth: partnership / recruiter credentials
- Pagination: TBD under export agreement

## Job list / page structure (if known)
- Content-Type: XML (export) or JSON (internal/partner — not public)
- Path to items / selectors: N/A until partnership spec received
- Key fields observed or documented: cadre-focused offers; NAF code, contract type, localized city rules for Paris/Lyon/Marseille arrondissements (recruiter docs)

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| numeroOffre | source_job_id | when exposed in export |
| url | url | apec.fr offer page |
| intitule | title | |
| entreprise | company | |
| description | description | |
| lieu | location | FR |
| salaire | salary_text | |
| typeContrat | job_type | |

## Geo / role fit
- Countries: FR (executives/cadres)
- Fit for FMI Demand Compass: FR senior market; pair with France Travail OAuth collector for broader FR public offers

## Gaps / next step
- Submit APEC “export XML” partnership request; clarify inbound data license for analytics
- Do not scrape search UI or third-party Apify actors (ADR-003)

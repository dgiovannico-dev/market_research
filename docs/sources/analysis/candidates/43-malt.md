# Malt (catalog_id=43)

| Field | Value |
|-------|-------|
| Analysis | PARTNER_ONLY |
| Category | B |
| verification_status | UNDER_REVIEW |
| access_mode | partner_or_unknown |
| connector_key | — |

## Official / docs
- Official: https://www.malt.com/
- Docs / developer: https://api.malt.com/ — Stoplight docs (freelancer billing, payments, fee invoices, SCIM provisioning).
- Terms / robots notes: Public API does **not** expose talent search, missions, or marketplace job listings. Enterprise integrations (SAP Fieldglass, Coupa, Workday P2P, etc.) are contractual.

## Access path (for future connector)
- Preferred: partner API / enterprise export — **not** suitable for open job-board ingest as catalog entry B.
- Endpoint candidates (method + URL):
  - Documented: `/freelancer/invoices`, `/freelancer/payments`, `/freelancer/fee-invoices`, `/scim/v2/Users` at `https://api.malt.com/` (identity-scoped token).
- Auth: `Authorization: {bare-api-token}` (per Malt docs; freelancer keys self-serve in account; client/org keys via Malt representative).
- Pagination: per resource in OpenAPI (not evaluated for Demand Compass).

## Job list / page structure (if known)
- Content-Type: n/a for listings — no public job list API documented.
- Marketplace roles/missions: web product only; **no authorized bulk listing path** for FMI crawlers (ADR-003).

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|
| — | — | No listing endpoint; do not scrape marketplace HTML |

## Geo / role fit
- Countries: FR/EU primary; enterprise buyers multi-country.
- Fit for FMI Demand Compass: indirect only via licensed exports or future partnership; not a runnable public connector today.

## Gaps / next step
- Reclassify catalog use-case: FMS/billing vs job corpus.
- If partnership adds mission/export feed, reopen with explicit authorization and schema.
- Until then: manual import or exclude from automated category B crawl.

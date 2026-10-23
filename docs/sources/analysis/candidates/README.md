# Candidate sources (no in-repo collector yet)

One sheet per catalog entry **without** a wired `connector_key` analysis under `../{key}.md`.

**File naming:** `{catalog_id}-{slug}.md` (slug = lowercase name, non-alnum → `-`).

**ADR-003:** document only authorized / public API / open-data / partner paths. Do **not** prescribe HTML scraping of Indeed, LinkedIn, or other ToS-blocked sites. Mark those `BLOCKED_TOS` in Analysis.

**IMPLEMENTED:** candidate was promoted to a live collector — keep this sheet for research history and link `Collector sheet` → `../{connector_key}.md`. Regenerate the index with `python3 backend/scripts/generate_candidates_index.py`.

## Template

```markdown
# {Name} (catalog_id={id})

| Field | Value |
|-------|-------|
| Analysis | TODO_ACCESS \| DOCUMENTED \| BLOCKED_TOS \| PARTNER_ONLY \| IMPLEMENTED |
| Category | A–I |
| verification_status | UNDER_REVIEW \| NEEDS_CREDENTIALS \| … |
| access_mode | from catalog |
| connector_key | — |

## Official / docs
- Official:
- Docs / developer:
- Terms / robots notes:

## Access path (for future connector)
- Preferred: public API | RSS/Atom | open data | partner API | none suitable
- Endpoint candidates (method + URL):
- Auth:
- Pagination:

## Job list / page structure (if known)
- Content-Type:
- Path to items / selectors:
- Key fields observed or documented:

## Field map sketch → RawJob
| Source | RawJob | Notes |
|--------|--------|-------|

## Geo / role fit
- Countries:
- Fit for FMI Demand Compass:

## Gaps / next step
- 
```

## Index

See [INDEX.md](INDEX.md).

## What to build next

Prioritized connector shortlist: [NEXT_CONNECTORS.md](../NEXT_CONNECTORS.md).

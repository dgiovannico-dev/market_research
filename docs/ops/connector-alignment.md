# Connector triple-truth alignment

Three representations must stay aligned for a connector to be runnable and honest:

| Truth | Location | Role |
|-------|----------|------|
| **Catalog SoR** | `data/sources/catalog.json` (+ generator under `backend/scripts/catalog_gen/`) | Candidate inventory, verification status, docs. Size ≠ coverage ([ADR-005](../decisions/ADR-005-global-source-catalog.md)). |
| **Registry** | `backend/app/collectors/registry.py` (`COLLECTORS`, modes, geo) | In-process adapters: `source_key` → `BaseCollector`. |
| **DB Source** | Postgres `sources` row (`connector_type`, `enabled`, `verification_status`, `connector_status`) | Runtime enablement; seed syncs from catalog. |

## Checklist (before marking ACTIVE)

1. Catalog entry exists with accurate `connector_key` / access mode ([ADR-003](../decisions/ADR-003-authorized-connectors-only.md)).
2. Collector registered under the same key; `collection_mode` correct (`search` \| `dump` \| `feed`).
3. Credentials: secrets bundle **or** ATS tenant CSV allowlist — do not confuse the two (`collectors/credentials.py`).
4. Seed / promote: DB `verification_status=ACTIVE` only after real insert evidence (`promote_source_active.py`).
5. Regenerate catalog if generator metadata changed; do not hand-edit ACTIVE without evidence.

## Anti-patterns

- Catalog `ACTIVE` without a registry adapter
- Env topic defaults as market control plane ([ADR-007](../decisions/ADR-007-query-first-sync.md))
- Treating catalog row count as market coverage

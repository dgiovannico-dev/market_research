# ADR-009: Keycloak identity + localStorage profile + admin-only secrets

## Status

Accepted

## Date

2026-10-24

## Context

Production needs distinct end users and admins. Connector API keys and platform config must stay ops-owned. End-user persona/prefs should not require a multi-tenant profile table in v1. Market job corpus stays shared (ADR-001, ADR-007).

## Decision

1. **Identity:** Keycloak OIDC. Realm roles `admin` and `user`. FastAPI validates Bearer JWT via JWKS when `OIDC_ENABLED=true`.
2. **Machine clients:** CronJob / smoke keep shared `API_KEY` (`X-API-Key`); not used by the browser.
3. **Admin secrets:** Credential PUT/DELETE and credential-fields require JWT role `admin`, with optional break-glass `OPS_API_TOKEN` when OIDC is off or as documented fallback.
4. **Admin UI:** When OIDC is on, Sources LLM admin + credential editor mount only for realm `admin` (`canSeeAdminConfig`). API remains authoritative (403 for non-admin).
5. **End-user profile:** Source of truth is **browser localStorage** (`fmi:userProfile:v1`, prefs `fmi:dashboardPrefs:v2`). Server `UserProfile` LIMIT-1 path is not the multi-user path.
6. **Skill gaps:** Client sends owned skill names in a POST body; API compares to observed market demand (no PII profile row required).

## Consequences

- Frontend must attach Bearer tokens; empty `API_KEY` alone is insufficient for browser prod when OIDC is on.
- Non-admin browsers do not see admin config panels; break-glass stays for automation/curl, not as a user-facing ops-token tease.
- No per-user connector keys in v1.
- Applications/alerts cross-device sync deferred.

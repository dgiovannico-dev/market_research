/** Whether browser UI may render ops admin config panels (LLM settings, credentials). */

export type AdminUiGate = {
  /** OIDC / Keycloak enabled for this build */
  enabled: boolean;
  isAdmin: boolean;
};

/**
 * With OIDC on: only realm role `admin` sees config panels (no ops-token tease for users).
 * With OIDC off: show panels for local/dev; mutations still need OPS_API_TOKEN.
 */
export function canSeeAdminConfig({ enabled, isAdmin }: AdminUiGate): boolean {
  if (enabled) return isAdmin;
  return true;
}

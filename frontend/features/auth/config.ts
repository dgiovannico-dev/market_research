/** Public OIDC / Keycloak settings (NEXT_PUBLIC_*). */

export type OidcPublicConfig = {
  enabled: boolean;
  url: string;
  realm: string;
  clientId: string;
};

export function getOidcConfig(): OidcPublicConfig {
  return {
    enabled: (process.env.NEXT_PUBLIC_OIDC_ENABLED || "").toLowerCase() === "true",
    url: (process.env.NEXT_PUBLIC_KEYCLOAK_URL || "").replace(/\/$/, ""),
    realm: process.env.NEXT_PUBLIC_KEYCLOAK_REALM || "fmi",
    clientId: process.env.NEXT_PUBLIC_OIDC_CLIENT_ID || "fmi-frontend",
  };
}

export function oidcEnabled(): boolean {
  const c = getOidcConfig();
  return c.enabled && Boolean(c.url && c.realm && c.clientId);
}

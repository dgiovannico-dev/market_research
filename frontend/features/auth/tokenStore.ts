const ACCESS_KEY = "fmi.oidc.accessToken";
const REFRESH_KEY = "fmi.oidc.refreshToken";

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  try {
    return sessionStorage.getItem(ACCESS_KEY);
  } catch {
    return null;
  }
}

export function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  try {
    return sessionStorage.getItem(REFRESH_KEY);
  } catch {
    return null;
  }
}

export function setTokens(access: string, refresh?: string | null) {
  if (typeof window === "undefined") return;
  try {
    sessionStorage.setItem(ACCESS_KEY, access);
    if (refresh) sessionStorage.setItem(REFRESH_KEY, refresh);
    else sessionStorage.removeItem(REFRESH_KEY);
  } catch {
    /* ignore */
  }
}

export function clearTokens() {
  if (typeof window === "undefined") return;
  try {
    sessionStorage.removeItem(ACCESS_KEY);
    sessionStorage.removeItem(REFRESH_KEY);
  } catch {
    /* ignore */
  }
}

/** Decode JWT payload (no verify — API verifies). */
export function decodeJwtPayload(token: string): Record<string, unknown> | null {
  try {
    const part = token.split(".")[1];
    if (!part) return null;
    const json = atob(part.replace(/-/g, "+").replace(/_/g, "/"));
    return JSON.parse(json) as Record<string, unknown>;
  } catch {
    return null;
  }
}

export function rolesFromAccessToken(token: string | null): string[] {
  if (!token) return [];
  const payload = decodeJwtPayload(token);
  if (!payload) return [];
  const roles = new Set<string>();
  const realm = payload.realm_access as { roles?: string[] } | undefined;
  for (const r of realm?.roles || []) roles.add(r);
  const resource = payload.resource_access as Record<string, { roles?: string[] }> | undefined;
  if (resource) {
    for (const client of Object.values(resource)) {
      for (const r of client?.roles || []) roles.add(r);
    }
  }
  return [...roles];
}

export function isAdminFromToken(token: string | null): boolean {
  return rolesFromAccessToken(token).includes("admin");
}

import { getOidcConfig, oidcEnabled } from "./config";
import { challengeS256, randomVerifier, storeVerifier, takeVerifier } from "./pkce";
import { clearTokens, getAccessToken, setTokens } from "./tokenStore";

function authBase(): string {
  const c = getOidcConfig();
  return `${c.url}/realms/${encodeURIComponent(c.realm)}/protocol/openid-connect`;
}

export function redirectUri(): string {
  if (typeof window === "undefined") return "";
  return `${window.location.origin}/auth/callback`;
}

export async function beginLogin(): Promise<void> {
  if (!oidcEnabled()) return;
  const c = getOidcConfig();
  const verifier = randomVerifier();
  storeVerifier(verifier);
  const challenge = await challengeS256(verifier);
  const params = new URLSearchParams({
    client_id: c.clientId,
    response_type: "code",
    scope: "openid profile email",
    redirect_uri: redirectUri(),
    code_challenge: challenge,
    code_challenge_method: "S256",
  });
  window.location.assign(`${authBase()}/auth?${params.toString()}`);
}

export async function finishLogin(code: string): Promise<void> {
  const c = getOidcConfig();
  const verifier = takeVerifier();
  if (!verifier) throw new Error("Missing PKCE verifier");
  const body = new URLSearchParams({
    grant_type: "authorization_code",
    client_id: c.clientId,
    code,
    redirect_uri: redirectUri(),
    code_verifier: verifier,
  });
  const res = await fetch(`${authBase()}/token`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
  if (!res.ok) throw new Error(`Token exchange failed: ${res.status}`);
  const data = (await res.json()) as {
    access_token?: string;
    refresh_token?: string;
  };
  if (!data.access_token) throw new Error("No access_token");
  setTokens(data.access_token, data.refresh_token);
}

export async function logout(): Promise<void> {
  const c = getOidcConfig();
  const token = getAccessToken();
  clearTokens();
  if (!oidcEnabled() || !token) {
    if (typeof window !== "undefined") window.location.assign("/");
    return;
  }
  const params = new URLSearchParams({
    client_id: c.clientId,
    post_logout_redirect_uri: typeof window !== "undefined" ? window.location.origin : "",
  });
  window.location.assign(`${authBase()}/logout?${params.toString()}`);
}

export function authHeaders(): Record<string, string> {
  const t = getAccessToken();
  if (!t) return {};
  return { Authorization: `Bearer ${t}` };
}

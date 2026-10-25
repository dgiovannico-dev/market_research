import { authHeaders, getAccessToken, isAdminFromToken } from "@/features/auth";
import { API_URL } from "@/shared/api";

function connectorBase(connectorKey: string) {
  return `${API_URL}/api/v1/ops/connectors/${encodeURIComponent(connectorKey)}`;
}

/** Admin JWT Bearer preferred; optional X-Ops-Token break-glass. */
function adminHeaders(opsToken: string, json = false): HeadersInit {
  const h: Record<string, string> = { ...authHeaders() };
  const t = opsToken.trim();
  if (t) h["X-Ops-Token"] = t;
  if (json) h["Content-Type"] = "application/json";
  return h;
}

export function canEditCredentials(opsToken: string): boolean {
  if (isAdminFromToken(getAccessToken())) return true;
  return Boolean(opsToken.trim());
}

export async function fetchCredentialFields(
  connectorKey: string,
  opsToken: string,
) {
  const res = await fetch(`${connectorBase(connectorKey)}/credential-fields`, {
    cache: "no-store",
    headers: adminHeaders(opsToken),
  });
  const data = await res.json().catch(() => ({}));
  return { res, data };
}

export async function putConnectorCredentials(
  connectorKey: string,
  opsToken: string,
  body: Record<string, unknown>,
) {
  const res = await fetch(`${connectorBase(connectorKey)}/credentials`, {
    method: "PUT",
    headers: adminHeaders(opsToken, true),
    body: JSON.stringify(body),
  });
  const data = await res.json().catch(() => ({}));
  return { res, data };
}

export async function deleteConnectorCredentials(
  connectorKey: string,
  opsToken: string,
) {
  const res = await fetch(`${connectorBase(connectorKey)}/credentials`, {
    method: "DELETE",
    headers: adminHeaders(opsToken),
  });
  const data = await res.json().catch(() => ({}));
  return { res, data };
}

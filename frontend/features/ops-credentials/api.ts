import { API_URL } from "@/shared/api";

function connectorBase(connectorKey: string) {
  return `${API_URL}/api/v1/ops/connectors/${encodeURIComponent(connectorKey)}`;
}

function opsHeaders(opsToken: string, json = false): HeadersInit {
  const h: Record<string, string> = { "X-Ops-Token": opsToken.trim() };
  if (json) h["Content-Type"] = "application/json";
  return h;
}

export async function fetchCredentialFields(
  connectorKey: string,
  opsToken: string,
) {
  const res = await fetch(`${connectorBase(connectorKey)}/credential-fields`, {
    cache: "no-store",
    headers: opsHeaders(opsToken),
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
    headers: opsHeaders(opsToken, true),
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
    headers: opsHeaders(opsToken),
  });
  const data = await res.json().catch(() => ({}));
  return { res, data };
}

export class ApiRequestError extends Error {
  readonly status: number;
  readonly path: string;

  constructor(path: string, status: number, detail?: string) {
    super(detail ?? `API ${path} failed: ${status}`);
    this.name = "ApiRequestError";
    this.status = status;
    this.path = path;
  }
}

/** Browser / public URL (host-reachable). */
const PUBLIC_API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Server Components / Route Handlers inside Docker must reach the API by
 * service name; the browser still uses NEXT_PUBLIC_API_URL (localhost).
 */
function resolveApiBase(): string {
  const internal = process.env.INTERNAL_API_URL?.trim();
  if (internal && typeof window === "undefined") return internal.replace(/\/$/, "");
  return PUBLIC_API_URL.replace(/\/$/, "");
}

const API_URL = PUBLIC_API_URL;

export async function requestJSON<T>(path: string, init?: RequestInit): Promise<T> {
  const base = resolveApiBase();
  const res = await fetch(`${base}${path}`, { cache: "no-store", ...init });
  if (!res.ok) {
    let detail: string | undefined;
    try {
      const body = (await res.json()) as { detail?: string };
      if (typeof body.detail === "string") detail = body.detail;
    } catch {
      /* ignore non-JSON error bodies */
    }
    throw new ApiRequestError(path, res.status, detail);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export async function getJSON<T>(path: string): Promise<T> {
  return requestJSON<T>(path);
}

export { API_URL, resolveApiBase };

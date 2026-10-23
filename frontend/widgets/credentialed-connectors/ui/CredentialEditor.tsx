"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import {
  deleteConnectorCredentials,
  fetchCredentialFields,
  putConnectorCredentials,
} from "@/features/ops-credentials";

const OPS_TOKEN_KEY = "fmi.opsApiToken";

type FieldMeta = {
  set: boolean;
  required: boolean;
};

type FieldsResponse = {
  connector_key: string;
  credentials_source: string;
  credentials_present: boolean;
  required: string[];
  fields: Record<string, FieldMeta>;
  updated_at: string | null;
};

type Props = {
  connectorKey: string;
  /** @deprecated Unused — requests go through `@/features/ops-credentials` + API_URL. */
  apiUrl?: string;
  onSaved: () => void;
  onClose: () => void;
};

function readOpsToken(): string {
  try {
    return sessionStorage.getItem(OPS_TOKEN_KEY) || "";
  } catch {
    return "";
  }
}

function writeOpsToken(token: string) {
  try {
    if (token) sessionStorage.setItem(OPS_TOKEN_KEY, token);
    else sessionStorage.removeItem(OPS_TOKEN_KEY);
  } catch {
    /* ignore */
  }
}

export function CredentialEditor({
  connectorKey,
  onSaved,
  onClose,
}: Props) {
  const t = useTranslations("sources");
  const [opsToken, setOpsToken] = useState("");
  const [meta, setMeta] = useState<FieldsResponse | null>(null);
  const [values, setValues] = useState<Record<string, string>>({});
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    setOpsToken(readOpsToken());
  }, []);

  useEffect(() => {
    if (!opsToken.trim()) {
      setMeta(null);
      return;
    }
    let cancelled = false;
    setError("");
    void fetchCredentialFields(connectorKey, opsToken)
      .then(({ res, data }) => {
        if (res.status === 401) {
          throw new Error(t("credOpsTokenInvalid"));
        }
        if (!res.ok) {
          throw new Error(
            (data as { detail?: string }).detail || res.statusText,
          );
        }
        if (!cancelled) {
          setMeta(data as FieldsResponse);
          const next: Record<string, string> = {};
          for (const name of Object.keys(
            (data as FieldsResponse).fields || {},
          )) {
            next[name] = "";
          }
          setValues(next);
        }
      })
      .catch((e) => {
        if (!cancelled) {
          setMeta(null);
          setError(e instanceof Error ? e.message : t("credLoadFailed"));
        }
      });
    return () => {
      cancelled = true;
    };
  }, [connectorKey, opsToken, t]);

  async function save() {
    setBusy(true);
    setError("");
    writeOpsToken(opsToken.trim());
    try {
      const payload: Record<string, string> = {};
      for (const [k, v] of Object.entries(values)) {
        if (v.trim()) payload[k] = v.trim();
      }
      const { res, data } = await putConnectorCredentials(
        connectorKey,
        opsToken,
        { fields: payload, ops_label: "ops-ui" },
      );
      if (res.status === 401) throw new Error(t("credOpsTokenInvalid"));
      if (!res.ok) {
        throw new Error(
          (data as { detail?: string }).detail || res.statusText,
        );
      }
      onSaved();
      onClose();
    } catch (e) {
      setError(e instanceof Error ? e.message : t("credSaveFailed"));
    } finally {
      setBusy(false);
    }
  }

  async function remove() {
    if (!window.confirm(t("credDeleteConfirm"))) return;
    setBusy(true);
    setError("");
    writeOpsToken(opsToken.trim());
    try {
      const { res, data } = await deleteConnectorCredentials(
        connectorKey,
        opsToken,
      );
      if (res.status === 401) throw new Error(t("credOpsTokenInvalid"));
      if (!res.ok) {
        throw new Error(
          (data as { detail?: string }).detail || res.statusText,
        );
      }
      onSaved();
      onClose();
    } catch (e) {
      setError(e instanceof Error ? e.message : t("credDeleteFailed"));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div
      className="mt-2 rounded border border-[var(--line)] bg-[var(--panel)] p-3 text-xs"
      role="region"
      aria-label={t("credEditorTitle", { key: connectorKey })}
    >
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="font-medium">
          {t("credEditorTitle", { key: connectorKey })}
        </p>
        <button
          type="button"
          className="opacity-70 hover:opacity-100"
          onClick={onClose}
        >
          {t("credEditorClose")}
        </button>
      </div>
      <label className="mt-2 block">
        <span className="opacity-70">{t("credOpsTokenLabel")}</span>
        <input
          type="password"
          autoComplete="off"
          className="mt-1 w-full rounded border border-[var(--line)] bg-transparent px-2 py-1"
          value={opsToken}
          onChange={(e) => setOpsToken(e.target.value)}
          placeholder={t("credOpsTokenPlaceholder")}
        />
      </label>
      <p className="mt-1 opacity-60">{t("credOpsTokenHint")}</p>
      {error ? <p className="mt-2 text-red-700">{error}</p> : null}
      {meta ? (
        <ul className="mt-3 space-y-2">
          {Object.entries(meta.fields).map(([name, info]) => (
            <li key={name}>
              <label className="block">
                <span className="opacity-80">
                  {name}
                  {info.required ? " *" : ""}
                  {info.set ? ` · ${t("credFieldSet")}` : ""}
                </span>
                <input
                  type="password"
                  autoComplete="off"
                  className="mt-1 w-full rounded border border-[var(--line)] bg-transparent px-2 py-1"
                  value={values[name] || ""}
                  onChange={(e) =>
                    setValues((prev) => ({ ...prev, [name]: e.target.value }))
                  }
                  placeholder={
                    info.set ? t("credFieldKeep") : t("credFieldEnter")
                  }
                />
              </label>
            </li>
          ))}
        </ul>
      ) : opsToken.trim() ? (
        <p className="mt-2 opacity-60">{t("credLoading")}</p>
      ) : (
        <p className="mt-2 opacity-60">{t("credOpsTokenNeeded")}</p>
      )}
      <div className="mt-3 flex flex-wrap gap-2">
        <button
          type="button"
          className="rounded border border-[var(--line)] px-2 py-1 disabled:opacity-40"
          disabled={busy || !opsToken.trim() || !meta}
          onClick={() => void save()}
        >
          {t("credSave")}
        </button>
        <button
          type="button"
          className="rounded border border-[var(--line)] px-2 py-1 text-red-800 disabled:opacity-40"
          disabled={busy || !opsToken.trim()}
          onClick={() => void remove()}
        >
          {t("credDeleteDb")}
        </button>
      </div>
    </div>
  );
}

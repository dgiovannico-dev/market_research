"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { canSeeAdminConfig, useAuth } from "@/features/auth";
import {
  activatePromptVersion,
  archivePromptVersion,
  canEditLlm,
  createPromptVersion,
  fetchLlmSettings,
  fetchPrompts,
  putLlmSettings,
  testLlm,
  type LlmSettings,
  type PromptTemplate,
} from "@/features/ops-llm-settings";

const OPS_TOKEN_KEY = "fmi.opsApiToken";

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

const PROVIDERS = ["none", "ollama", "openai_compatible", "gemini"] as const;

export function LlmAdminPanel() {
  const t = useTranslations("llmAdmin");
  const { isAdmin, enabled: oidcOn } = useAuth();
  const visible = canSeeAdminConfig({ enabled: oidcOn, isAdmin });
  const [opsToken, setOpsToken] = useState("");
  const [settings, setSettings] = useState<LlmSettings | null>(null);
  const [prompts, setPrompts] = useState<PromptTemplate[]>([]);
  const [apiKey, setApiKey] = useState("");
  const [error, setError] = useState("");
  const [status, setStatus] = useState("");
  const [busy, setBusy] = useState(false);
  const [draftSlug, setDraftSlug] = useState("classify_job");
  const [draftSystem, setDraftSystem] = useState("");
  const [draftUser, setDraftUser] = useState("");
  const allowed = visible && (canEditLlm(opsToken) || isAdmin);

  useEffect(() => {
    setOpsToken(readOpsToken());
  }, []);

  async function reload() {
    if (!allowed) return;
    setError("");
    const [s, p] = await Promise.all([
      fetchLlmSettings(opsToken),
      fetchPrompts(opsToken),
    ]);
    if (s.res.status === 401 || p.res.status === 401) {
      setError(t("tokenInvalid"));
      return;
    }
    if (!s.res.ok) {
      setError(String((s.data as { detail?: string }).detail || s.res.statusText));
      return;
    }
    setSettings(s.data as LlmSettings);
    if (p.res.ok) setPrompts(p.data.items || []);
  }

  useEffect(() => {
    if (!allowed) {
      setSettings(null);
      setPrompts([]);
      return;
    }
    void reload();
    // eslint-disable-next-line react-hooks/exhaustive-deps -- reload when auth gate changes
  }, [allowed, opsToken]);

  async function saveSettings() {
    if (!settings) return;
    setBusy(true);
    setError("");
    setStatus("");
    try {
      const body: Record<string, unknown> = {
        provider: settings.provider,
        base_url: settings.base_url,
        model: settings.model,
        temperature: settings.temperature,
        timeout_s: settings.timeout_s,
        max_tokens: settings.max_tokens,
        enable_classify: settings.enable_classify,
        enable_weekly_report: settings.enable_weekly_report,
        enable_study_advisor: settings.enable_study_advisor,
        enable_brief_narrative: settings.enable_brief_narrative,
      };
      if (apiKey.trim()) body.api_key = apiKey.trim();
      const { res, data } = await putLlmSettings(opsToken, body);
      if (!res.ok) throw new Error(String((data as { detail?: string }).detail || res.statusText));
      setApiKey("");
      setSettings(data as LlmSettings);
      setStatus(t("saved"));
    } catch (e) {
      setError(e instanceof Error ? e.message : t("failed"));
    } finally {
      setBusy(false);
    }
  }

  async function runTest() {
    setBusy(true);
    setError("");
    try {
      const { res, data } = await testLlm(opsToken);
      if (!res.ok) throw new Error(String((data as { detail?: string }).detail || res.statusText));
      setStatus(JSON.stringify(data).slice(0, 400));
    } catch (e) {
      setError(e instanceof Error ? e.message : t("failed"));
    } finally {
      setBusy(false);
    }
  }

  async function cloneAndActivate() {
    setBusy(true);
    setError("");
    try {
      const { res, data } = await createPromptVersion(opsToken, draftSlug, {
        system_text: draftSystem,
        user_text: draftUser,
        notes: "ops ui",
        activate: true,
      });
      if (!res.ok) throw new Error(String((data as { detail?: string }).detail || res.statusText));
      setStatus(t("promptActivated", { version: String((data as { version?: number }).version ?? "") }));
      await reload();
    } catch (e) {
      setError(e instanceof Error ? e.message : t("failed"));
    } finally {
      setBusy(false);
    }
  }

  if (!visible) return null;

  return (
    <section className="mt-6 space-y-4 border-t border-[var(--line)] pt-4">
      <h3 className="font-semibold text-[var(--ink)]">{t("title")}</h3>
      <p className="text-sm text-[var(--muted)]">{t("subtitle")}</p>

      {!oidcOn && !isAdmin ? (
        <label className="block text-sm">
          <span className="text-[var(--muted)]">{t("opsToken")}</span>
          <input
            type="password"
            className="mt-1 w-full max-w-md rounded border border-[var(--line)] bg-transparent px-2 py-1"
            value={opsToken}
            onChange={(e) => {
              const v = e.target.value;
              setOpsToken(v);
              writeOpsToken(v);
            }}
            autoComplete="off"
          />
        </label>
      ) : null}

      {!allowed ? (
        <p className="text-sm text-[var(--muted)]">{t("needAdmin")}</p>
      ) : null}

      {error ? <p className="text-sm text-red-600">{error}</p> : null}
      {status ? <pre className="overflow-x-auto text-xs opacity-70">{status}</pre> : null}

      {settings ? (
        <div className="grid gap-3 sm:grid-cols-2">
          <label className="text-sm">
            {t("provider")}
            <select
              className="mt-1 w-full rounded border border-[var(--line)] bg-transparent px-2 py-1"
              value={settings.provider}
              onChange={(e) =>
                setSettings({ ...settings, provider: e.target.value })
              }
            >
              {PROVIDERS.map((p) => (
                <option key={p} value={p}>
                  {p}
                </option>
              ))}
            </select>
          </label>
          <label className="text-sm">
            {t("model")}
            <input
              className="mt-1 w-full rounded border border-[var(--line)] bg-transparent px-2 py-1"
              value={settings.model || ""}
              onChange={(e) => setSettings({ ...settings, model: e.target.value })}
            />
          </label>
          <label className="text-sm sm:col-span-2">
            {t("baseUrl")}
            <input
              className="mt-1 w-full rounded border border-[var(--line)] bg-transparent px-2 py-1"
              value={settings.base_url || ""}
              onChange={(e) =>
                setSettings({ ...settings, base_url: e.target.value })
              }
            />
          </label>
          <label className="text-sm sm:col-span-2">
            {t("apiKey")}{" "}
            <span className="text-[var(--muted)]">
              {settings.api_key_set ? t("keySet") : t("keyUnset")}
            </span>
            <input
              type="password"
              className="mt-1 w-full rounded border border-[var(--line)] bg-transparent px-2 py-1"
              value={apiKey}
              placeholder={t("keyPlaceholder")}
              onChange={(e) => setApiKey(e.target.value)}
              autoComplete="off"
            />
          </label>
          {(
            [
              ["enable_classify", t("flagClassify")],
              ["enable_weekly_report", t("flagWeekly")],
              ["enable_study_advisor", t("flagStudy")],
              ["enable_brief_narrative", t("flagBrief")],
            ] as const
          ).map(([key, label]) => (
            <label key={key} className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={Boolean(settings[key])}
                onChange={(e) =>
                  setSettings({ ...settings, [key]: e.target.checked })
                }
              />
              {label}
            </label>
          ))}
          <div className="flex flex-wrap gap-2 sm:col-span-2">
            <button
              type="button"
              disabled={busy}
              onClick={() => void saveSettings()}
              className="rounded border border-[var(--line)] px-3 py-2 text-sm hover:border-[var(--signal)] disabled:opacity-50"
            >
              {t("save")}
            </button>
            <button
              type="button"
              disabled={busy}
              onClick={() => void runTest()}
              className="rounded border border-[var(--line)] px-3 py-2 text-sm hover:border-[var(--signal)] disabled:opacity-50"
            >
              {t("test")}
            </button>
          </div>
          <p className="text-xs text-[var(--muted)] sm:col-span-2">
            {t("sourceLine", { source: settings.source })}
          </p>
        </div>
      ) : null}

      {prompts.length > 0 ? (
        <div className="space-y-3">
          <h4 className="font-medium">{t("promptsTitle")}</h4>
          <ul className="space-y-2 text-sm">
            {prompts.map((tmpl) => (
              <li key={tmpl.slug} className="border-b border-[var(--line)] pb-2">
                <div className="font-medium">
                  {tmpl.slug}{" "}
                  <span className="text-xs text-[var(--muted)]">
                    ({tmpl.purpose})
                  </span>
                </div>
                <ul className="mt-1 space-y-1 text-xs text-[var(--muted)]">
                  {tmpl.versions.map((v) => (
                    <li key={v.id} className="flex flex-wrap items-center gap-2">
                      <span>
                        v{v.version} · {v.status}
                      </span>
                      {v.status !== "active" ? (
                        <>
                          <button
                            type="button"
                            disabled={busy}
                            className="underline"
                            onClick={() =>
                              void activatePromptVersion(opsToken, v.id).then(
                                reload,
                              )
                            }
                          >
                            {t("activate")}
                          </button>
                          {v.status !== "archived" ? (
                            <button
                              type="button"
                              disabled={busy}
                              className="underline"
                              onClick={() =>
                                void archivePromptVersion(opsToken, v.id).then(
                                  reload,
                                )
                              }
                            >
                              {t("archive")}
                            </button>
                          ) : null}
                        </>
                      ) : null}
                    </li>
                  ))}
                </ul>
              </li>
            ))}
          </ul>

          <div className="space-y-2 rounded border border-[var(--line)] p-3">
            <p className="text-sm font-medium">{t("newVersion")}</p>
            <select
              className="w-full rounded border border-[var(--line)] bg-transparent px-2 py-1 text-sm"
              value={draftSlug}
              onChange={(e) => {
                setDraftSlug(e.target.value);
                const tmpl = prompts.find((p) => p.slug === e.target.value);
                const active =
                  tmpl?.versions.find((v) => v.id === tmpl.active_version_id) ||
                  tmpl?.versions[0];
                if (active) {
                  setDraftSystem(active.system_text);
                  setDraftUser(active.user_text);
                }
              }}
            >
              {prompts.map((p) => (
                <option key={p.slug} value={p.slug}>
                  {p.slug}
                </option>
              ))}
            </select>
            <textarea
              className="h-20 w-full rounded border border-[var(--line)] bg-transparent px-2 py-1 text-xs"
              value={draftSystem}
              onChange={(e) => setDraftSystem(e.target.value)}
              placeholder={t("systemPh")}
            />
            <textarea
              className="h-20 w-full rounded border border-[var(--line)] bg-transparent px-2 py-1 text-xs"
              value={draftUser}
              onChange={(e) => setDraftUser(e.target.value)}
              placeholder={t("userPh")}
            />
            <button
              type="button"
              disabled={busy || !draftSystem}
              onClick={() => void cloneAndActivate()}
              className="rounded border border-[var(--line)] px-3 py-2 text-sm hover:border-[var(--signal)] disabled:opacity-50"
            >
              {t("saveActivate")}
            </button>
          </div>
        </div>
      ) : null}
    </section>
  );
}

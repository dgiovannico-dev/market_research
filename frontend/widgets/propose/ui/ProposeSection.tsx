"use client";

import { useLocale, useTranslations } from "next-intl";
import { useState } from "react";
import { api, type AssistantLocale } from "@/lib/api";
import { useDashboardPrefs } from "@/features/dashboard-prefs";

export function ProposeSection() {
  const t = useTranslations("assistant");
  const locale = useLocale() as AssistantLocale;
  const { applyDashboardSpec, prefs } = useDashboardPrefs();
  const [prompt, setPrompt] = useState("");
  const [kind, setKind] = useState<"dashboard" | "report">("dashboard");
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const run = async () => {
    setBusy(true);
    setError(null);
    try {
      const data = await api.assistantPropose(
        prompt,
        kind,
        kind === "report",
        locale,
      );
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : t("proposeFailed"));
    } finally {
      setBusy(false);
    }
  };

  const apply = () => {
    if (!result || result.kind !== "dashboard") return;
    const spec = result.spec as {
      period_days?: number;
      view_mode?: "guided" | "trends_only";
      filters?: { technologies?: string[]; countries?: string[] };
    };
    applyDashboardSpec(spec);
  };

  return (
    <div className="space-y-4">
      <section className="card space-y-3 p-5">
        <header className="space-y-1">
          <h2 className="font-display text-xl font-semibold tracking-tight text-[var(--ink)]">
            {t("title")}
          </h2>
          <p className="text-sm text-[var(--muted)]">
            {t("subtitle", { viewMode: prefs.view_mode, days: prefs.period_days })}
          </p>
        </header>
        <textarea
          className="min-h-24 w-full rounded-md border border-[var(--line)] bg-transparent p-3 text-sm text-[var(--ink)] placeholder:text-[var(--muted)] focus:border-[var(--signal)] focus:outline-none"
          value={prompt}
          placeholder={t("promptPlaceholder")}
          onChange={(e) => setPrompt(e.target.value)}
        />
        <div className="flex flex-wrap gap-2">
          <select
            className="rounded-md border border-[var(--line)] bg-transparent px-2 py-1.5 text-sm text-[var(--ink)] focus:border-[var(--signal)] focus:outline-none"
            value={kind}
            onChange={(e) => setKind(e.target.value as "dashboard" | "report")}
          >
            <option value="dashboard">{t("kindDashboard")}</option>
            <option value="report">{t("kindReport")}</option>
          </select>
          <button
            type="button"
            disabled={busy || !prompt.trim()}
            className="rounded-md bg-[var(--signal)] px-3 py-1.5 text-sm font-medium text-white transition-opacity hover:opacity-90 disabled:opacity-50"
            onClick={() => void run()}
          >
            {busy ? t("working") : t("propose")}
          </button>
          {result?.kind === "dashboard" ? (
            <button
              type="button"
              className="rounded-md border border-[var(--line)] px-3 py-1.5 text-sm text-[var(--ink)] transition-colors hover:border-[var(--signal)] hover:text-[var(--signal)]"
              onClick={apply}
            >
              {t("applyPrefs")}
            </button>
          ) : null}
        </div>
        {error ? <p className="text-sm text-[var(--warn)]">{error}</p> : null}
      </section>

      {result ? (
        <section className="card space-y-3 p-5">
          <h3 className="font-display text-base font-semibold tracking-tight text-[var(--ink)]">
            {t("resultTitle")}
          </h3>
          <pre className="overflow-x-auto font-mono text-xs text-[var(--muted)]">
            {JSON.stringify(result, null, 2)}
          </pre>
          {result.materialized &&
          typeof result.materialized === "object" &&
          result.materialized !== null &&
          "narrative" in result.materialized ? (
            <p className="text-sm text-[var(--ink)]">
              {(result.materialized as { narrative: string }).narrative}
            </p>
          ) : null}
        </section>
      ) : null}
    </div>
  );
}

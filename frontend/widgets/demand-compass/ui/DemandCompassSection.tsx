"use client";

import { Suspense, useState } from "react";
import { useLocale, useTranslations } from "next-intl";
import {
  ASSISTANT_BRIEF_TYPES,
  briefChipKey,
} from "@/features/propose-watch";
import { BriefResult } from "./BriefResult";
import { useDashboardCountries } from "@/features/country-filter";
import {
  LensToggle,
  useDashboardLens,
} from "@/features/lens-toggle";
import { useDashboardPrefs } from "@/features/dashboard-prefs";
import {
  api,
  type AssistantBriefType,
  type AssistantLocale,
  type EvidenceBrief,
} from "@/lib/api";

function DemandCompassInner() {
  const t = useTranslations("assistant");
  const tCompass = useTranslations("compass");
  const locale = useLocale() as AssistantLocale;
  const { prefs } = useDashboardPrefs();
  const { lens, queryIds } = useDashboardLens();
  const { countries } = useDashboardCountries();
  const [active, setActive] = useState<AssistantBriefType | null>(null);
  const [brief, setBrief] = useState<EvidenceBrief | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const runBrief = async (briefType: AssistantBriefType) => {
    setBusy(true);
    setError(null);
    setActive(briefType);
    try {
      const data = await api.assistantBrief({
        brief_type: briefType,
        lens: briefType === "focus_vs_market" ? "compare" : lens,
        query_ids: queryIds.length > 0 ? queryIds : undefined,
        period_days: prefs.period_days,
        country_code: countries.length ? countries.join(",") : undefined,
        locale,
      });
      setBrief(data.brief);
    } catch (e) {
      setBrief(null);
      setError(e instanceof Error ? e.message : t("briefFailed"));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="space-y-4">
      <section className="card space-y-3 p-5">
        <header className="space-y-1">
          <p className="font-display text-xs uppercase tracking-[0.2em] signal-text">
            {tCompass("briefEyebrow")}
          </p>
          <h2 className="font-display text-xl font-semibold tracking-tight text-[var(--ink)]">
            {t("compassTitle")}
          </h2>
          <p className="text-sm text-[var(--muted)]">{t("compassSubtitle")}</p>
        </header>

        <div className="flex flex-wrap items-center gap-3">
          <LensToggle.Control />
          <span className="text-xs text-[var(--muted)]">
            {t("periodDays", { days: prefs.period_days })}
            {countries.length > 0
              ? ` · ${countries.join(", ")}`
              : null}
          </span>
        </div>

        <div
          className="flex flex-wrap gap-2"
          role="group"
          aria-label={t("briefChipsAria")}
        >
          {ASSISTANT_BRIEF_TYPES.map((briefType) => {
            const selected = active === briefType;
            return (
              <button
                key={briefType}
                type="button"
                disabled={busy}
                aria-pressed={selected}
                className={`rounded-full border px-3 py-1.5 text-sm font-medium transition-colors duration-200 disabled:opacity-50 ${
                  selected
                    ? "border-[var(--signal)] bg-[var(--signal)] text-white"
                    : "border-[var(--line)] text-[var(--ink)] hover:border-[var(--signal)] hover:text-[var(--signal)]"
                }`}
                onClick={() => void runBrief(briefType)}
              >
                {tCompass(briefChipKey(briefType))}
              </button>
            );
          })}
        </div>

        {busy ? <p className="text-sm text-[var(--muted)]">{t("briefWorking")}</p> : null}
        {error ? <p className="text-sm text-[var(--warn)]">{error}</p> : null}
      </section>
      {brief && !busy ? <BriefResult brief={brief} /> : null}
    </div>
  );
}

export function DemandCompassSection() {
  const t = useTranslations("assistant");
  return (
    <Suspense
      fallback={
        <div className="card p-5 text-sm text-[var(--muted)]">{t("briefWorking")}</div>
      }
    >
      <LensToggle.Provider>
        <DemandCompassInner />
      </LensToggle.Provider>
    </Suspense>
  );
}

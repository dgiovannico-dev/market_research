"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";
import { useLocalProfile } from "@/features/user-profile";
import { useDashboardPrefs } from "@/features/dashboard-prefs";
import { useDashboardCountries } from "@/features/country-filter";
import { WatchCandidates } from "@/features/propose-watch";
import type { ProposedWatchCandidate } from "@/entities/assistant";
import {
  loadStudyPlan,
  saveStudyPlan,
  studyAdvisorApi,
  studyPlanToIcs,
  type StudyModality,
  type StudyPlan,
} from "@/entities/study-advisor";

const MODALITIES: StudyModality[] = [
  "employed_part_time",
  "freelance_full_time",
  "intensive",
];

export function StudyAdvisorDashboard() {
  const t = useTranslations("studyAdvisor");
  const { profile, hydrated: profileReady } = useLocalProfile();
  const { prefs, hydrated: prefsReady } = useDashboardPrefs();
  const { countries } = useDashboardCountries();
  const guided = prefs.view_mode === "guided";

  const [hours, setHours] = useState(6);
  const [modality, setModality] = useState<StudyModality>("employed_part_time");
  const [horizon, setHorizon] = useState(8);
  const [plan, setPlan] = useState<StudyPlan | null>(null);
  const [evidence, setEvidence] = useState<Record<string, unknown> | null>(null);
  const [mode, setMode] = useState<string>("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [refineMsg, setRefineMsg] = useState("");
  const [watchCandidates, setWatchCandidates] = useState<ProposedWatchCandidate[]>(
    [],
  );

  useEffect(() => {
    const stored = loadStudyPlan();
    if (stored?.plan) {
      setPlan(stored.plan);
      setEvidence(stored.evidence);
      setHours(stored.plan.hours_per_week);
      setModality(stored.plan.modality);
      setHorizon(stored.plan.horizon_weeks);
    }
  }, []);

  if (!prefsReady || !profileReady) {
    return <p className="text-sm text-[var(--muted)]">{t("loading")}</p>;
  }

  if (!guided) {
    return (
      <div className="rounded-xl border border-[var(--line)] bg-[var(--card)] p-6 text-sm text-[var(--muted)]">
        {t("trendsOnlyHidden")}
      </div>
    );
  }

  async function generate() {
    setBusy(true);
    setError("");
    try {
      const res = await studyAdvisorApi.plan({
        skills: profile.skills,
        certifications: profile.certifications,
        hours_per_week: hours,
        modality,
        horizon_weeks: horizon,
        country_code: countries.length ? countries.join(",") : undefined,
        days: Math.min(Math.max(prefs.period_days, 7), 365),
      });
      setPlan(res.plan);
      setEvidence(res.evidence);
      setMode(res.mode + (res.reason ? ` (${res.reason})` : ""));
      saveStudyPlan(res.plan, res.evidence);
    } catch (e) {
      setError(e instanceof Error ? e.message : t("failed"));
    } finally {
      setBusy(false);
    }
  }

  async function refine() {
    if (!plan || !evidence || !refineMsg.trim()) return;
    setBusy(true);
    setError("");
    try {
      const res = await studyAdvisorApi.refine({
        plan,
        evidence,
        message: refineMsg.trim(),
      });
      if (res.plan) {
        setPlan(res.plan);
        saveStudyPlan(res.plan, evidence);
        setMode(res.mode || "refine");
        setRefineMsg("");
      }
      if (res.status === "skipped") {
        setError(t("refineSkipped"));
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : t("failed"));
    } finally {
      setBusy(false);
    }
  }

  function exportIcs() {
    if (!plan) return;
    const blob = new Blob([studyPlanToIcs(plan)], {
      type: "text/calendar;charset=utf-8",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "fmi-study-plan.ics";
    a.click();
    URL.revokeObjectURL(url);
  }

  function suggestWatch(tech: string) {
    setWatchCandidates((prev) => {
      if (prev.some((p) => p.query_text === tech)) return prev;
      return [
        ...prev,
        {
          name: `Watch ${tech}`,
          query_text: tech,
          kind: "focus",
          rationale: t("watchRationale", { tech }),
          support: undefined,
          origin_hint: "llm_suggest",
        },
      ];
    });
  }

  return (
    <div className="space-y-6">
      <header className="space-y-1">
        <h1 className="text-xl font-semibold text-[var(--ink)]">{t("title")}</h1>
        <p className="text-sm text-[var(--muted)]">{t("subtitle")}</p>
        <p className="text-xs text-[var(--muted)]">
          <Link href="/stack" className="underline">
            {t("openStack")}
          </Link>
          {" · "}
          <Link href="/profile" className="underline">
            {t("openProfile")}
          </Link>
        </p>
      </header>

      {profile.skills.length < 3 ? (
        <p className="rounded border border-[var(--line)] p-3 text-sm text-[var(--muted)]">
          {t("needSkills")}
        </p>
      ) : null}

      <section className="grid gap-3 sm:grid-cols-3">
        <label className="text-sm">
          {t("hours")}
          <input
            type="number"
            min={1}
            max={80}
            className="mt-1 w-full rounded border border-[var(--line)] bg-transparent px-2 py-1"
            value={hours}
            onChange={(e) => setHours(Number(e.target.value) || 6)}
          />
        </label>
        <label className="text-sm">
          {t("modality")}
          <select
            className="mt-1 w-full rounded border border-[var(--line)] bg-transparent px-2 py-1"
            value={modality}
            onChange={(e) => setModality(e.target.value as StudyModality)}
          >
            {MODALITIES.map((m) => (
              <option key={m} value={m}>
                {t(`modality_${m}`)}
              </option>
            ))}
          </select>
        </label>
        <label className="text-sm">
          {t("horizon")}
          <input
            type="number"
            min={1}
            max={52}
            className="mt-1 w-full rounded border border-[var(--line)] bg-transparent px-2 py-1"
            value={horizon}
            onChange={(e) => setHorizon(Number(e.target.value) || 8)}
          />
        </label>
      </section>

      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          disabled={busy || profile.skills.length < 1}
          onClick={() => void generate()}
          className="rounded border border-[var(--line)] px-3 py-2 text-sm hover:border-[var(--signal)] disabled:opacity-50"
        >
          {busy ? t("generating") : t("generate")}
        </button>
        {plan ? (
          <>
            <button
              type="button"
              onClick={exportIcs}
              className="rounded border border-[var(--line)] px-3 py-2 text-sm hover:border-[var(--signal)]"
            >
              {t("exportIcs")}
            </button>
            <button
              type="button"
              onClick={() => plan && evidence && saveStudyPlan(plan, evidence)}
              className="rounded border border-[var(--line)] px-3 py-2 text-sm hover:border-[var(--signal)]"
            >
              {t("saveLocal")}
            </button>
          </>
        ) : null}
      </div>

      {error ? <p className="text-sm text-red-600">{error}</p> : null}
      {mode ? (
        <p className="text-xs text-[var(--muted)]">
          {t("modeLine", { mode })}
        </p>
      ) : null}

      {plan ? (
        <section className="space-y-4 rounded-xl border border-[var(--line)] bg-[var(--card)] p-4">
          <h2 className="font-semibold">{plan.title}</h2>
          <p className="text-sm text-[var(--muted)]">
            {t("planMeta", {
              weeks: String(plan.horizon_weeks),
              hours: String(plan.hours_per_week),
              source: plan.source,
            })}
          </p>
          <div>
            <h3 className="text-sm font-medium">{t("stackTarget")}</h3>
            <ul className="mt-1 flex flex-wrap gap-2">
              {plan.stack_target.map((tech) => (
                <li key={tech}>
                  <button
                    type="button"
                    className="rounded-full border border-[var(--line)] px-3 py-1 text-xs hover:border-[var(--signal)]"
                    onClick={() => suggestWatch(tech)}
                  >
                    {tech} · {t("suggestWatch")}
                  </button>
                </li>
              ))}
              {plan.stack_target.length === 0 ? (
                <li className="text-xs text-[var(--muted)]">{t("emptyStack")}</li>
              ) : null}
            </ul>
          </div>
          <div>
            <h3 className="text-sm font-medium">{t("milestones")}</h3>
            <ol className="mt-2 list-decimal space-y-2 pl-5 text-sm">
              {plan.milestones.map((m, i) => (
                <li key={`${m.week}-${i}`}>
                  <span className="font-medium">
                    W{m.week}: {m.title}
                  </span>
                  <span className="text-[var(--muted)]">
                    {" "}
                    — {(m.skills || []).join(", ")}
                  </span>
                </li>
              ))}
            </ol>
          </div>
          {plan.limits?.length ? (
            <div>
              <h3 className="text-sm font-medium">{t("limits")}</h3>
              <ul className="mt-1 list-disc space-y-1 pl-5 text-xs text-[var(--muted)]">
                {plan.limits.map((l) => (
                  <li key={l}>{l}</li>
                ))}
              </ul>
            </div>
          ) : null}

          <div className="space-y-2 border-t border-[var(--line)] pt-3">
            <label className="block text-sm">
              {t("refineLabel")}
              <input
                className="mt-1 w-full rounded border border-[var(--line)] bg-transparent px-2 py-1"
                value={refineMsg}
                onChange={(e) => setRefineMsg(e.target.value)}
                placeholder={t("refinePh")}
              />
            </label>
            <button
              type="button"
              disabled={busy || !refineMsg.trim()}
              onClick={() => void refine()}
              className="rounded border border-[var(--line)] px-3 py-2 text-sm hover:border-[var(--signal)] disabled:opacity-50"
            >
              {t("refine")}
            </button>
          </div>
        </section>
      ) : null}

      {watchCandidates.length > 0 ? (
        <WatchCandidates candidates={watchCandidates} />
      ) : null}
    </div>
  );
}

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
  loadBusySlots,
  loadStudyPlan,
  saveBusySlots,
  saveStudyPlan,
  studyAdvisorApi,
  studyPlanToIcs,
  type BusySlot,
  type StudyModality,
  type StudyPlan,
} from "@/entities/study-advisor";
import { BusySlotsEditor } from "./BusySlotsEditor";
import { CalendarFeedSync } from "./CalendarFeedSync";
import { StudyPlanCard } from "./StudyPlanCard";
import { WeekCalendar } from "./WeekCalendar";

const MODALITIES: StudyModality[] = [
  "employed_part_time",
  "freelance_full_time",
  "intensive",
];

function humanLimit(
  raw: string,
  t: (key: string, values?: Record<string, string>) => string,
): string {
  const s = raw.trim();
  if (/learning candidates combine/i.test(s)) return t("limitCorpus");
  if (/gap-only candidate/i.test(s)) return t("limitGapOnly");
  if (/co-occurrence and gap scores/i.test(s)) return t("limitScores");
  if (s === "schedule_no_window" || /no free study window/i.test(s)) {
    return t("limitNoWindow");
  }
  const wlb = /^schedule_wlb_days:(\d+)$/.exec(s);
  if (wlb) {
    return t("limitWlb", { days: wlb[1] });
  }
  const partial = /^schedule_partial:(\d+):(\d+)$/.exec(s);
  if (partial) {
    const got = Number(partial[1]);
    const want = Number(partial[2]);
    return t("limitPartial", {
      gotH: String(Math.floor(got / 60)),
      gotM: String(got % 60).padStart(2, "0"),
      wantH: String(Math.floor(want / 60)),
    });
  }
  if (/could only fit about/i.test(s)) return s;
  if (/dropped ungrounded/i.test(s)) return t("limitDropped");
  if (/llm fallback/i.test(s)) return t("limitLlmFallback");
  if (/insufficient_data/i.test(s)) return t("limitThin");
  if (/no learning candidates/i.test(s)) return t("limitNoCandidates");
  return s;
}

export function StudyAdvisorDashboard() {
  const t = useTranslations("studyAdvisor");
  const { profile, hydrated: profileReady } = useLocalProfile();
  const { prefs, hydrated: prefsReady } = useDashboardPrefs();
  const { countries } = useDashboardCountries();
  const guided = prefs.view_mode === "guided";

  const [hours, setHours] = useState(6);
  const [modality, setModality] = useState<StudyModality>("employed_part_time");
  const [horizon, setHorizon] = useState(8);
  const [busySlots, setBusySlots] = useState<BusySlot[]>([]);
  const [plan, setPlan] = useState<StudyPlan | null>(null);
  const [evidence, setEvidence] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [refineMsg, setRefineMsg] = useState("");
  const [watchCandidates, setWatchCandidates] = useState<ProposedWatchCandidate[]>(
    [],
  );

  useEffect(() => {
    setBusySlots(loadBusySlots());
    const stored = loadStudyPlan();
    if (stored?.plan) {
      setPlan(stored.plan);
      setEvidence(stored.evidence);
      setHours(stored.plan.hours_per_week);
      setModality(stored.plan.modality);
      setHorizon(stored.plan.horizon_weeks);
    }
  }, []);

  function updateBusy(next: BusySlot[]) {
    setBusySlots(next);
    saveBusySlots(next);
  }

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

  async function generate(slots: BusySlot[] = busySlots) {
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
        busy_slots: slots,
      });
      setPlan(res.plan);
      setEvidence(res.evidence);
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
        evidence: { ...evidence, busy_slots: busySlots },
        message: refineMsg.trim(),
      });
      if (res.plan) {
        const refreshed = await studyAdvisorApi.plan({
          skills: profile.skills,
          certifications: profile.certifications,
          hours_per_week: res.plan.hours_per_week,
          modality: res.plan.modality,
          horizon_weeks: res.plan.horizon_weeks,
          country_code: countries.length ? countries.join(",") : undefined,
          days: Math.min(Math.max(prefs.period_days, 7), 365),
          busy_slots: busySlots,
        });
        const merged: StudyPlan = {
          ...refreshed.plan,
          title: res.plan.title || refreshed.plan.title,
          stack_target: res.plan.stack_target?.length
            ? res.plan.stack_target
            : refreshed.plan.stack_target,
          milestones: res.plan.milestones?.length
            ? res.plan.milestones
            : refreshed.plan.milestones,
          weekly_template: refreshed.plan.weekly_template,
        };
        setPlan(merged);
        setEvidence(refreshed.evidence);
        saveStudyPlan(merged, refreshed.evidence);
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

  const limits = (plan?.limits || [])
    .map((l) => humanLimit(l, t))
    .filter((l, i, arr) => l && arr.indexOf(l) === i);

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

      <BusySlotsEditor slots={busySlots} onChange={updateBusy} />

      <CalendarFeedSync
        busySlots={busySlots}
        onBusyChange={updateBusy}
        onReplan={(slots) => generate(slots)}
        disabled={busy || profile.skills.length < 1}
      />

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

      {plan ? (
        <>
          <WeekCalendar
            studySlots={plan.weekly_template || []}
            busySlots={busySlots}
          />
          <StudyPlanCard
            plan={plan}
            limits={limits}
            refineMsg={refineMsg}
            onRefineMsg={setRefineMsg}
            onRefine={() => void refine()}
            onSuggestWatch={suggestWatch}
            busy={busy}
          />
        </>
      ) : null}

      {watchCandidates.length > 0 ? (
        <WatchCandidates candidates={watchCandidates} />
      ) : null}
    </div>
  );
}

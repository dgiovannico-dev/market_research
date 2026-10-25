"use client";

import { useTranslations } from "next-intl";
import type { StudyMilestone, StudyPlan } from "@/entities/study-advisor";

type Props = {
  plan: StudyPlan;
  limits: string[];
  refineMsg: string;
  onRefineMsg: (v: string) => void;
  onRefine: () => void;
  onSuggestWatch: (tech: string) => void;
  busy: boolean;
};

function skillsPhrase(skills: string[], andWord: string): string {
  if (skills.length === 0) return "";
  if (skills.length === 1) return skills[0];
  if (skills.length === 2) return `${skills[0]} ${andWord} ${skills[1]}`;
  return `${skills.slice(0, -1).join(", ")} ${andWord} ${skills[skills.length - 1]}`;
}

type TFn = (key: string, values?: Record<string, string>) => string;

function milestoneCopy(
  m: StudyMilestone,
  t: TFn,
): { weekLabel: string; body: string } {
  const weekLabel = t("milestoneWeek", { week: String(m.week) });
  const skills = m.skills || [];
  const generic = /^milestone\s*\d+$/i.test((m.title || "").trim());
  if (generic && skills.length) {
    return {
      weekLabel,
      body: t("milestoneFocusBody", {
        skills: skillsPhrase(skills, t("andWord")),
      }),
    };
  }
  if (skills.length && m.title) {
    return {
      weekLabel,
      body: t("milestoneTitledBody", {
        title: m.title,
        skills: skillsPhrase(skills, t("andWord")),
      }),
    };
  }
  return { weekLabel, body: m.title || t("milestoneFallback") };
}

export function StudyPlanCard({
  plan,
  limits,
  refineMsg,
  onRefineMsg,
  onRefine,
  onSuggestWatch,
  busy,
}: Props) {
  const t = useTranslations("studyAdvisor");
  const stack = plan.stack_target || [];
  const headline =
    stack.length > 0
      ? t("planHeadline", {
          skills: skillsPhrase(stack.slice(0, 3), t("andWord")),
          weeks: String(plan.horizon_weeks),
        })
      : t("planHeadlineEmpty");

  return (
    <section className="space-y-5 rounded-xl border border-[var(--line)] bg-[var(--card)] p-5">
      <header className="space-y-2">
        <p className="text-[11px] font-medium uppercase tracking-wide text-[var(--muted)]">
          {t("planEyebrow")}
        </p>
        <h2 className="text-lg font-semibold leading-snug text-[var(--ink)]">
          {headline}
        </h2>
        <p className="text-sm text-[var(--muted)]">
          {t("planMetaHuman", {
            weeks: String(plan.horizon_weeks),
            hours: String(plan.hours_per_week),
            modality: t(`modality_${plan.modality}`),
          })}
        </p>
      </header>

      <div>
        <h3 className="text-sm font-medium text-[var(--ink)]">{t("stackTarget")}</h3>
        <p className="mt-0.5 text-xs text-[var(--muted)]">{t("stackHint")}</p>
        <ul className="mt-3 flex flex-wrap gap-2">
          {stack.map((tech) => (
            <li key={tech}>
              <button
                type="button"
                className="rounded-md border border-[var(--line)] px-3 py-1.5 text-sm hover:border-[var(--signal)]"
                onClick={() => onSuggestWatch(tech)}
              >
                {tech}
                <span className="ml-1.5 text-xs text-[var(--muted)]">
                  {t("suggestWatch")}
                </span>
              </button>
            </li>
          ))}
          {stack.length === 0 ? (
            <li className="text-sm text-[var(--muted)]">{t("emptyStack")}</li>
          ) : null}
        </ul>
      </div>

      <div>
        <h3 className="text-sm font-medium text-[var(--ink)]">{t("milestones")}</h3>
        <p className="mt-0.5 text-xs text-[var(--muted)]">{t("milestonesHint")}</p>
        <ol className="mt-3 space-y-3">
          {plan.milestones.map((m, i) => {
            const copy = milestoneCopy(m, t);
            return (
              <li
                key={`${m.week}-${i}`}
                className="border-l-2 border-[color-mix(in_srgb,var(--signal)_50%,transparent)] pl-3"
              >
                <p className="text-xs font-medium uppercase tracking-wide text-[var(--muted)]">
                  {copy.weekLabel}
                </p>
                <p className="text-sm text-[var(--ink)]">{copy.body}</p>
              </li>
            );
          })}
          {plan.milestones.length === 0 ? (
            <li className="text-sm text-[var(--muted)]">{t("milestonesEmpty")}</li>
          ) : null}
        </ol>
      </div>

      {limits.length ? (
        <div>
          <h3 className="text-sm font-medium text-[var(--ink)]">{t("limits")}</h3>
          <ul className="mt-2 space-y-1.5 text-sm text-[var(--muted)]">
            {limits.map((l) => (
              <li key={l} className="flex gap-2">
                <span aria-hidden className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-[var(--muted)]" />
                <span>{l}</span>
              </li>
            ))}
          </ul>
        </div>
      ) : null}

      <div className="space-y-2 border-t border-[var(--line)] pt-4">
        <label className="block text-sm">
          {t("refineLabel")}
          <input
            className="mt-1 w-full rounded border border-[var(--line)] bg-transparent px-2 py-1.5"
            value={refineMsg}
            onChange={(e) => onRefineMsg(e.target.value)}
            placeholder={t("refinePh")}
          />
        </label>
        <button
          type="button"
          disabled={busy || !refineMsg.trim()}
          onClick={onRefine}
          className="rounded border border-[var(--line)] px-3 py-2 text-sm hover:border-[var(--signal)] disabled:opacity-50"
        >
          {t("refine")}
        </button>
      </div>
    </section>
  );
}

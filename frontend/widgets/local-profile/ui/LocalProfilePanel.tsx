"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";
import {
  parseSkillsCsv,
  useLocalProfile,
} from "@/features/user-profile";
import { syncFocusTechnologiesFromSkills } from "@/features/user-profile/syncFocusTechnologies";
import { useDashboardPrefs } from "@/features/dashboard-prefs";
import { requestJSON } from "@/shared/api/http";

type GapsResponse = {
  gaps?: Array<Record<string, unknown>>;
  owned_skills?: string[];
  disclaimer?: string;
  error?: string;
};

type RecsResponse = {
  items?: Array<Record<string, unknown>>;
  disclaimer?: string;
  error?: string;
};

export function LocalProfilePanel() {
  const t = useTranslations("profile");
  const { profile, setProfile, hydrated } = useLocalProfile();
  const { prefs } = useDashboardPrefs();
  const guided = prefs.view_mode === "guided";
  const [skillsRaw, setSkillsRaw] = useState("");
  const [certsRaw, setCertsRaw] = useState("");
  const [gaps, setGaps] = useState<GapsResponse>({});
  const [recs, setRecs] = useState<RecsResponse>({});
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (!hydrated) return;
    setSkillsRaw(profile.skills.join(", "));
    setCertsRaw(profile.certifications.join(", "));
  }, [hydrated, profile.skills, profile.certifications]);

  async function analyze() {
    setError(null);
    const skills = parseSkillsCsv(skillsRaw);
    const certifications = parseSkillsCsv(certsRaw);
    const next = { ...profile, skills, certifications };
    setProfile(next);
    syncFocusTechnologiesFromSkills(skills);
    setSaved(true);
    try {
      const [g, r] = await Promise.all([
        requestJSON<GapsResponse>("/api/v1/profile/skill-gaps", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ skills }),
        }),
        requestJSON<RecsResponse>("/api/v1/profile/recommendations", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ skills }),
        }),
      ]);
      setGaps(g);
      setRecs(r);
    } catch (e) {
      setError(e instanceof Error ? e.message : t("loadFailed"));
    }
  }

  function persistField<K extends keyof typeof profile>(
    key: K,
    value: (typeof profile)[K],
  ) {
    setProfile({ ...profile, [key]: value });
    setSaved(true);
  }

  const gapItems = gaps.gaps || [];
  const recItems = recs.items || [];

  return (
    <div className="space-y-5">
      <header className="space-y-1">
        <h2 className="font-display text-2xl font-semibold tracking-tight text-[var(--ink)]">
          {t("title")}
        </h2>
        <p className="text-sm text-[var(--muted)]">{t("localStorageHint")}</p>
        {saved ? (
          <p className="text-xs text-[var(--signal)]">{t("savedLocal")}</p>
        ) : null}
        {error ? (
          <p className="text-sm text-[var(--warn)]" role="alert">
            {error}
          </p>
        ) : null}
      </header>

      <section className="space-y-3 rounded-xl border border-[var(--line)] bg-[var(--card)] p-4">
        <label className="block text-sm">
          <span className="opacity-70">{t("fieldName")}</span>
          <input
            className="mt-1 w-full rounded border border-[var(--line)] bg-transparent px-2 py-1.5"
            value={profile.display_name}
            onChange={(e) => persistField("display_name", e.target.value)}
          />
        </label>
        <label className="block text-sm">
          <span className="opacity-70">{t("fieldCountry")}</span>
          <input
            className="mt-1 w-full rounded border border-[var(--line)] bg-transparent px-2 py-1.5"
            value={profile.residence_country}
            onChange={(e) => persistField("residence_country", e.target.value)}
          />
        </label>
        <div className="flex flex-wrap gap-3 text-sm">
          <label className="min-w-[8rem] flex-1">
            <span className="opacity-70">{t("fieldRate")}</span>
            <input
              className="mt-1 w-full rounded border border-[var(--line)] bg-transparent px-2 py-1.5"
              value={profile.target_rate_amount}
              onChange={(e) => persistField("target_rate_amount", e.target.value)}
            />
          </label>
          <label className="w-24">
            <span className="opacity-70">{t("fieldCurrency")}</span>
            <input
              className="mt-1 w-full rounded border border-[var(--line)] bg-transparent px-2 py-1.5"
              value={profile.rate_currency}
              onChange={(e) => persistField("rate_currency", e.target.value)}
            />
          </label>
          <label className="w-24">
            <span className="opacity-70">{t("fieldUnit")}</span>
            <input
              className="mt-1 w-full rounded border border-[var(--line)] bg-transparent px-2 py-1.5"
              value={profile.rate_unit}
              onChange={(e) => persistField("rate_unit", e.target.value)}
            />
          </label>
        </div>
        <label className="block text-sm">
          <span className="opacity-70">{t("fieldSkills")}</span>
          <textarea
            className="mt-1 w-full rounded border border-[var(--line)] bg-transparent px-2 py-1.5 font-mono text-xs"
            rows={3}
            value={skillsRaw}
            onChange={(e) => setSkillsRaw(e.target.value)}
            placeholder="Python, Kubernetes, AWS"
          />
        </label>
        <label className="block text-sm">
          <span className="opacity-70">{t("fieldCerts")}</span>
          <textarea
            className="mt-1 w-full rounded border border-[var(--line)] bg-transparent px-2 py-1.5 font-mono text-xs"
            rows={2}
            value={certsRaw}
            onChange={(e) => setCertsRaw(e.target.value)}
            placeholder="CKAD, AWS SAA"
          />
        </label>
        <div className="flex flex-wrap items-center gap-3">
          <button
            type="button"
            className="rounded-full bg-[var(--signal)] px-4 py-2 text-sm text-white"
            onClick={() => void analyze()}
          >
            {t("analyzeGaps")}
          </button>
          {guided ? (
            <Link
              href="/stack"
              className="text-sm text-[var(--signal)] underline-offset-2 hover:underline"
            >
              {t("openStackCompass")}
            </Link>
          ) : null}
        </div>
      </section>

      {gaps.disclaimer ? (
        <p className="text-xs text-[var(--muted)]">{gaps.disclaimer}</p>
      ) : null}

      <section className="rounded-xl border border-[var(--line)] bg-[var(--card)] p-4">
        <h3 className="font-display text-base font-semibold tracking-tight text-[var(--ink)]">
          {t("gapsTitle")}
        </h3>
        {gapItems.length === 0 ? (
          <p className="mt-3 text-sm text-[var(--muted)]">{t("gapsEmpty")}</p>
        ) : (
          <ul className="mt-3 space-y-2 text-sm">
            {gapItems.slice(0, 15).map((g) => (
              <li
                key={String(g.technology)}
                className="flex justify-between border-b border-[var(--line)] py-1.5 last:border-b-0"
              >
                <span className="text-[var(--ink)]">
                  {String(g.technology)}{" "}
                  <span className="text-xs text-[var(--muted)]">
                    ({String(g.gap_type)})
                  </span>
                </span>
                <span className="font-mono text-xs">{String(g.priority_score)}</span>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="rounded-xl border border-[var(--line)] bg-[var(--card)] p-4">
        <h3 className="font-display text-base font-semibold tracking-tight text-[var(--ink)]">
          {t("recsTitle")}
        </h3>
        {recItems.length === 0 ? (
          <p className="mt-3 text-sm text-[var(--muted)]">{t("recsEmpty")}</p>
        ) : (
          <ul className="mt-3 space-y-2 text-sm">
            {recItems.slice(0, 10).map((item) => (
              <li key={String(item.job_id)} className="border-b border-[var(--line)] py-1.5 last:border-b-0">
                <span className="text-[var(--ink)]">{String(item.title)}</span>
                <span className="ml-2 text-xs text-[var(--muted)]">
                  match {String(item.skill_match)}
                </span>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}

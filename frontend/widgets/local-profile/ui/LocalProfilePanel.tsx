"use client";

import { useMemo, useState } from "react";
import { useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";
import {
  normalizeCountryCode,
  normalizeCurrency,
  normalizeRateUnit,
  profileCountryOptions,
  PROFILE_CURRENCIES,
  PROFILE_RATE_UNITS,
  useLocalProfile,
} from "@/features/user-profile";
import { syncFocusTechnologiesFromSkills } from "@/features/user-profile/syncFocusTechnologies";
import { useDashboardPrefs } from "@/features/dashboard-prefs";
import { requestJSON } from "@/shared/api/http";
import { ProfileTagField } from "./ProfileTagField";

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

const fieldClass =
  "mt-1 w-full rounded-md border border-[var(--line)] bg-transparent px-2 py-1.5 text-sm text-[var(--ink)] focus:border-[var(--signal)] focus:outline-none";

export function LocalProfilePanel() {
  const t = useTranslations("profile");
  const { profile, setProfile, hydrated } = useLocalProfile();
  const { prefs } = useDashboardPrefs();
  const guided = prefs.view_mode === "guided";
  const [gaps, setGaps] = useState<GapsResponse>({});
  const [recs, setRecs] = useState<RecsResponse>({});
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  const countries = useMemo(() => profileCountryOptions(), []);
  const residence = normalizeCountryCode(profile.residence_country);
  const currency = normalizeCurrency(profile.rate_currency);
  const unit = normalizeRateUnit(profile.rate_unit);

  function persistField<K extends keyof typeof profile>(
    key: K,
    value: (typeof profile)[K],
  ) {
    setProfile({ ...profile, [key]: value });
    setSaved(true);
  }

  async function analyze() {
    setError(null);
    const next = {
      ...profile,
      residence_country: residence,
      rate_currency: currency,
      rate_unit: unit,
      skills: profile.skills,
      certifications: profile.certifications,
    };
    setProfile(next);
    syncFocusTechnologiesFromSkills(next.skills);
    setSaved(true);
    try {
      const [g, r] = await Promise.all([
        requestJSON<GapsResponse>("/api/v1/profile/skill-gaps", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ skills: next.skills }),
        }),
        requestJSON<RecsResponse>("/api/v1/profile/recommendations", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ skills: next.skills }),
        }),
      ]);
      setGaps(g);
      setRecs(r);
    } catch (e) {
      setError(e instanceof Error ? e.message : t("loadFailed"));
    }
  }

  const gapItems = gaps.gaps || [];
  const recItems = recs.items || [];

  if (!hydrated) {
    return (
      <p className="text-sm text-[var(--muted)]">{t("loadingProfile")}</p>
    );
  }

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

      <section className="space-y-4 rounded-xl border border-[var(--line)] bg-[var(--card)] p-4">
        <label className="block text-sm">
          <span className="text-[var(--muted)]">{t("fieldName")}</span>
          <input
            className={fieldClass}
            value={profile.display_name}
            onChange={(e) => persistField("display_name", e.target.value)}
            autoComplete="name"
          />
        </label>

        <label className="block text-sm">
          <span className="text-[var(--muted)]">{t("fieldCountry")}</span>
          <select
            className={fieldClass}
            value={residence}
            onChange={(e) =>
              persistField("residence_country", normalizeCountryCode(e.target.value))
            }
          >
            <option value="">{t("countryPlaceholder")}</option>
            {countries.map((c) => (
              <option key={c.code} value={c.code}>
                {c.label}
              </option>
            ))}
          </select>
        </label>

        <div className="grid gap-3 sm:grid-cols-3">
          <label className="block text-sm">
            <span className="text-[var(--muted)]">{t("fieldRate")}</span>
            <input
              type="number"
              inputMode="decimal"
              min={0}
              step={1}
              className={fieldClass}
              value={profile.target_rate_amount}
              placeholder={t("ratePlaceholder")}
              onChange={(e) => {
                const v = e.target.value;
                if (v === "" || /^\d*([.,]\d*)?$/.test(v)) {
                  persistField("target_rate_amount", v.replace(",", "."));
                }
              }}
            />
          </label>
          <label className="block text-sm">
            <span className="text-[var(--muted)]">{t("fieldCurrency")}</span>
            <select
              className={fieldClass}
              value={currency}
              onChange={(e) =>
                persistField("rate_currency", normalizeCurrency(e.target.value))
              }
            >
              {PROFILE_CURRENCIES.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </label>
          <label className="block text-sm">
            <span className="text-[var(--muted)]">{t("fieldUnit")}</span>
            <select
              className={fieldClass}
              value={unit}
              onChange={(e) =>
                persistField("rate_unit", normalizeRateUnit(e.target.value))
              }
            >
              {PROFILE_RATE_UNITS.map((u) => (
                <option key={u} value={u}>
                  {t(`unit_${u}`)}
                </option>
              ))}
            </select>
          </label>
        </div>

        <ProfileTagField
          label={t("fieldSkills")}
          hint={t("skillsHint")}
          values={profile.skills}
          onChange={(skills) => persistField("skills", skills)}
          placeholder={t("skillsPlaceholder")}
          addLabel={t("addTag")}
        />
        <ProfileTagField
          label={t("fieldCerts")}
          hint={t("certsHint")}
          values={profile.certifications}
          onChange={(certifications) => persistField("certifications", certifications)}
          placeholder={t("certsPlaceholder")}
          addLabel={t("addTag")}
        />

        <div className="flex flex-wrap items-center gap-3 pt-1">
          <button
            type="button"
            className="rounded-md bg-[var(--signal)] px-4 py-2 text-sm font-medium text-white transition-opacity hover:opacity-90"
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
              <li
                key={String(item.job_id)}
                className="border-b border-[var(--line)] py-1.5 last:border-b-0"
              >
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

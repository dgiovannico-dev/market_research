"use client";

import { Suspense, useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";
import { useLocalProfile } from "@/features/user-profile";
import { useDashboardPrefs } from "@/features/dashboard-prefs";
import { useDashboardCountries } from "@/features/country-filter";
import {
  LensToggle,
  useDashboardLens,
} from "@/features/lens-toggle";
import { MarketCoverageBanner, PeriodChip } from "@/features/dashboard-chrome";
import { WatchCandidates } from "@/features/propose-watch";
import {
  stackCompassApi,
  type LearningCandidate,
  type LearningCandidatesPayload,
  type RelatedCert,
} from "@/entities/stack-compass";
import type { ProposedWatchCandidate } from "@/entities/assistant";

function limitsText(limits: LearningCandidate["limits"]): string {
  if (Array.isArray(limits)) return limits.join(" ");
  return limits || "";
}

function CandidateRow({
  c,
  onWatch,
}: {
  c: LearningCandidate;
  onWatch: (tech: string) => void;
}) {
  const t = useTranslations("stackCompass");
  const seed = c.drilldown?.relations_seed || c.technology;
  const rate = c.rate_check;
  return (
    <li className="space-y-2 border-b border-[var(--line)] py-3 last:border-b-0">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <div>
          <p className="font-medium text-[var(--ink)]">{c.technology}</p>
          <p className="text-xs text-[var(--muted)]">
            {c.anchor_skill
              ? t("anchor", { skill: c.anchor_skill })
              : t("gapOnly")}
            {typeof c.support === "number" ? ` · n=${c.support}` : null}
            {c.rise_cool_status ? ` · ${c.rise_cool_status}` : null}
          </p>
        </div>
        <div className="text-right font-mono text-xs text-[var(--ink)]">
          <div>
            {t("score")}:{" "}
            {(c.score ?? c.irreplaceability_score ?? 0).toFixed(3)}
          </div>
          {typeof c.irreplaceability_score === "number" ? (
            <div className="text-[var(--muted)]">
              irr={c.irreplaceability_score.toFixed(3)}
            </div>
          ) : null}
        </div>
      </div>
      {guidedExplain(c, t)}
      {rate?.status === "ok" && rate.rate?.median != null ? (
        <p className="text-xs text-[var(--muted)]">
          {t("rateOk", {
            median: String(rate.rate.median),
            n: String(rate.sample_size ?? 0),
          })}
        </p>
      ) : rate?.status === "insufficient_data" ? (
        <p className="text-xs text-[var(--muted)]">{t("rateThin")}</p>
      ) : null}
      <div className="flex flex-wrap gap-2">
        <Link
          href={`/relations?view=graph&seed=${encodeURIComponent(seed)}`}
          className="rounded-full border border-[var(--line)] px-3 py-1 text-xs text-[var(--ink)] hover:border-[var(--signal)]"
        >
          {t("openRelations")}
        </Link>
        <Link
          href="/certifications"
          className="rounded-full border border-[var(--line)] px-3 py-1 text-xs text-[var(--ink)] hover:border-[var(--signal)]"
        >
          {t("openCerts")}
        </Link>
        <button
          type="button"
          className="rounded-full bg-[var(--signal)] px-3 py-1 text-xs text-white"
          onClick={() => onWatch(c.technology)}
        >
          {t("addWatch")}
        </button>
      </div>
      {limitsText(c.limits) ? (
        <p className="text-[10px] text-[var(--muted)]">{limitsText(c.limits)}</p>
      ) : null}
    </li>
  );
}

function guidedExplain(
  c: LearningCandidate,
  t: ReturnType<typeof useTranslations<"stackCompass">>,
) {
  return (
    <p className="text-xs text-[var(--muted)]">
      {t("whyScore", {
        complement: String(c.complement ?? "—"),
        rarity: String(c.rarity_proxy ?? "—"),
        penalty: String(c.generic_penalty ?? "—"),
      })}
    </p>
  );
}

function CandidateList({
  title,
  items,
  onWatch,
}: {
  title: string;
  items: LearningCandidate[];
  onWatch: (tech: string) => void;
}) {
  if (items.length === 0) return null;
  return (
    <section className="rounded-xl border border-[var(--line)] bg-[var(--card)] p-4">
      <h3 className="font-display text-base font-semibold tracking-tight text-[var(--ink)]">
        {title}
      </h3>
      <ul className="mt-2">
        {items.map((c) => (
          <CandidateRow key={c.technology} c={c} onWatch={onWatch} />
        ))}
      </ul>
    </section>
  );
}

function StackCompassInner() {
  const t = useTranslations("stackCompass");
  const { profile, hydrated: profileReady } = useLocalProfile();
  const { prefs, hydrated: prefsReady } = useDashboardPrefs();
  const { lens, queryIds } = useDashboardLens();
  const { countries } = useDashboardCountries();
  const guided = prefs.view_mode === "guided";
  const [data, setData] = useState<LearningCandidatesPayload | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [watchCandidates, setWatchCandidates] = useState<ProposedWatchCandidate[]>(
    [],
  );

  useEffect(() => {
    if (!prefsReady || !profileReady) return;
    if (!guided) return;
    if (profile.skills.length < 1) {
      setData(null);
      return;
    }
    let cancelled = false;
    const days = Math.min(Math.max(prefs.period_days, 7), 365);
    stackCompassApi
      .learningCandidates(
        {
          skills: profile.skills,
          certifications: profile.certifications,
          country_code: countries.length ? countries.join(",") : undefined,
          days,
          top_n: 12,
        },
        { days, lens, queryIds, countries },
      )
      .then((payload) => {
        if (!cancelled) {
          setData(payload);
          setError(null);
        }
      })
      .catch((e) => {
        if (!cancelled) {
          setData(null);
          setError(e instanceof Error ? e.message : t("loadFailed"));
        }
      });
    return () => {
      cancelled = true;
    };
  }, [
    prefsReady,
    profileReady,
    guided,
    profile.skills,
    profile.certifications,
    prefs.period_days,
    lens,
    queryIds,
    countries,
    t,
  ]);

  const queueWatch = (tech: string) => {
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
  };

  if (!guided) {
    return (
      <div className="rounded-xl border border-[var(--line)] bg-[var(--card)] p-6 text-sm text-[var(--muted)]">
        {t("trendsOnlyHidden")}
      </div>
    );
  }

  const sample =
    data?.sample_size ??
    data?.jobs_analyzed ??
    data?.market?.sample_size ??
    null;

  const marketItems: LearningCandidate[] =
    data?.lens === "compare"
      ? data.market?.candidates ?? []
      : data?.candidates ?? [];
  const focusItems: LearningCandidate[] =
    data?.lens === "compare" ? data.focus?.candidates ?? [] : [];
  const related: RelatedCert[] =
    data?.related_certifications ??
    data?.market?.related_certifications ??
    [];

  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-end justify-between gap-3">
        <div className="space-y-1">
          <h2 className="font-display text-2xl font-semibold tracking-tight text-[var(--ink)]">
            {t("title")}
          </h2>
          <p className="max-w-2xl text-sm text-[var(--muted)]">{t("subtitle")}</p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <PeriodChip />
          <LensToggle.Control />
        </div>
      </header>

      <MarketCoverageBanner sampleSize={typeof sample === "number" ? sample : null} />

      {profile.skills.length < 3 ? (
        <p className="rounded-xl border border-[var(--line)] bg-[var(--card)] px-4 py-3 text-sm text-[var(--muted)]">
          {t("needSkills")}{" "}
          <Link href="/profile" className="text-[var(--signal)] underline-offset-2 hover:underline">
            {t("editProfile")}
          </Link>
        </p>
      ) : null}

      {error ? (
        <p className="text-sm text-[var(--warn)]" role="alert">
          {error}
        </p>
      ) : null}

      {data?.disclaimer ? (
        <p className="text-xs text-[var(--muted)]">{data.disclaimer}</p>
      ) : null}

      <p className="text-xs text-[var(--muted)]">{t("notVanity")}</p>

      {data?.lens === "compare" ? (
        <>
          <CandidateList
            title={t("marketCandidates")}
            items={marketItems.slice(0, 8)}
            onWatch={queueWatch}
          />
          <CandidateList
            title={t("focusCandidates")}
            items={focusItems.slice(0, 8)}
            onWatch={queueWatch}
          />
        </>
      ) : (
        <CandidateList
          title={t("candidates")}
          items={marketItems.slice(0, 10)}
          onWatch={queueWatch}
        />
      )}

      {related.length > 0 ? (
        <section className="rounded-xl border border-[var(--line)] bg-[var(--card)] p-4">
          <h3 className="font-display text-base font-semibold tracking-tight text-[var(--ink)]">
            {t("relatedCerts")}
          </h3>
          <ul className="mt-2 space-y-1 text-sm">
            {related.map((c) => (
              <li key={c.slug || c.display_name} className="flex justify-between">
                <span>{c.display_name || c.slug}</span>
                <span className="font-mono text-xs text-[var(--muted)]">
                  n={c.mentions ?? "—"}
                </span>
              </li>
            ))}
          </ul>
          <Link
            href="/certifications"
            className="mt-3 inline-block text-xs text-[var(--signal)] underline-offset-2 hover:underline"
          >
            {t("openCerts")}
          </Link>
        </section>
      ) : null}

      {watchCandidates.length > 0 ? (
        <section className="rounded-xl border border-[var(--line)] bg-[var(--card)] p-4">
          <WatchCandidates candidates={watchCandidates} />
        </section>
      ) : null}
    </div>
  );
}

export function StackCompassDashboard() {
  const t = useTranslations("common");
  return (
    <Suspense
      fallback={
        <div className="rounded-xl border border-[var(--line)] bg-[var(--card)] p-6 text-sm text-[var(--muted)]">
          {t("loading")}
        </div>
      }
    >
      <LensToggle.Provider>
        <StackCompassInner />
      </LensToggle.Provider>
    </Suspense>
  );
}

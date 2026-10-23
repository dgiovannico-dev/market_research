"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { useDashboardLens } from "@/features/lens-toggle";
import { DiscoveryCoverageWarn } from "@/features/research-intents";
import { Link } from "@/i18n/navigation";
import { researchApi } from "@/entities/research-intent";

/** Soft floor for observed market n — below this, treat as thin market. */
const THIN_MARKET_SAMPLE = 30;

type Props = {
  /** Observed sample size for the current market lens period (unique jobs or trend sum). */
  sampleSize: number | null;
};

/**
 * Inline (non-card) warning on market lens when discovery coverage or sample is thin.
 * Charts stay mounted; this only advises. Must render under LensToggle.Provider.
 */
export function MarketCoverageBanner({ sampleSize }: Props) {
  const { lens } = useDashboardLens();
  const t = useTranslations("compass");
  const [enabledCount, setEnabledCount] = useState<number | null>(null);

  useEffect(() => {
    if (lens !== "market") return;
    let cancelled = false;
    researchApi
      .list("discovery")
      .then((data) => {
        if (!cancelled) {
          setEnabledCount(data.items.filter((it) => it.enabled).length);
        }
      })
      .catch(() => {
        if (!cancelled) setEnabledCount(null);
      });
    return () => {
      cancelled = true;
    };
  }, [lens]);

  if (lens !== "market") return null;

  const lowDiscovery = enabledCount != null && enabledCount < 3;
  const thinSample = sampleSize != null && sampleSize < THIN_MARKET_SAMPLE;
  if (!lowDiscovery && !thinSample) return null;

  return (
    <div className="space-y-2" role="status">
      {lowDiscovery && enabledCount != null ? (
        <DiscoveryCoverageWarn enabledCount={enabledCount} />
      ) : null}
      {thinSample ? (
        <p className="rounded-lg border border-[var(--warn)]/40 bg-[color-mix(in_srgb,var(--warn)_12%,transparent)] px-3 py-2 text-sm text-[var(--warn)]">
          {t("thinMarketWarn", { n: sampleSize ?? 0 })}
        </p>
      ) : null}
      <p className="text-sm">
        <Link
          href="/market-scan"
          className="underline decoration-[var(--warn)]/50 underline-offset-2 hover:decoration-[var(--warn)]"
        >
          {t("coverageOpenScan")}
        </Link>
      </p>
    </div>
  );
}

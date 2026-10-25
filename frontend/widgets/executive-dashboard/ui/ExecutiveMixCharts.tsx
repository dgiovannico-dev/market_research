"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import {
  DonutMixLazy,
  RankBarsLazy,
} from "@/shared/ui/charts";
import {
  api,
  type MarketCertifications,
  type MarketFacets,
  type MarketLanguages,
} from "@/lib/api";
import type { DashboardLens } from "@/lib/api";
import { useRouter } from "@/i18n/navigation";

type Props = {
  periodDays: number;
  lens: DashboardLens;
  queryIds?: number[];
  countries?: string[];
  techItems: { technology: string; job_skill_mentions: number }[];
  techSampleSize?: number | null;
};

function unwrapFacets(data: MarketFacets | null): MarketFacets | null {
  if (!data) return null;
  if (data.lens === "compare") return data.market ?? null;
  return data;
}

function unwrapLangs(data: MarketLanguages | null): MarketLanguages | null {
  if (!data) return null;
  if (data.lens === "compare") return data.market ?? null;
  return data;
}

function unwrapCerts(
  data: MarketCertifications | null,
): MarketCertifications | null {
  if (!data) return null;
  if (data.lens === "compare") return data.market ?? null;
  return data;
}

export function ExecutiveMixCharts({
  periodDays,
  lens,
  queryIds,
  countries,
  techItems,
  techSampleSize = null,
}: Props) {
  const t = useTranslations("charts");
  const tExec = useTranslations("executive");
  const router = useRouter();
  const [facets, setFacets] = useState<MarketFacets | null>(null);
  const [langs, setLangs] = useState<MarketLanguages | null>(null);
  const [certs, setCerts] = useState<MarketCertifications | null>(null);

  useEffect(() => {
    let cancelled = false;
    const opts = { days: periodDays, lens, queryIds, countries };
    Promise.all([
      api.facets(opts),
      api.languages(opts),
      api.certificationsTop(opts),
    ])
      .then(([f, l, c]) => {
        if (!cancelled) {
          setFacets(f);
          setLangs(l);
          setCerts(c);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setFacets(null);
          setLangs(null);
          setCerts(null);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [periodDays, lens, queryIds, countries]);

  const facetBody = unwrapFacets(facets);
  const langBody = unwrapLangs(langs);
  const certBody = unwrapCerts(certs);
  const remote = facetBody?.facets?.remote ?? [];
  const contract = facetBody?.facets?.contract ?? [];
  const langItems = (langBody?.items ?? []).map((it) => ({
    label: it.language,
    value: it.jobs,
  }));
  const techRank = techItems.map((it) => ({
    label: it.technology,
    value: it.job_skill_mentions,
  }));
  const certRank = (certBody?.items ?? []).map((it) => ({
    label: it.certification,
    value: it.job_mentions,
  }));

  return (
    <div className="space-y-4">
      <div className="grid gap-4 lg:grid-cols-2">
        <DonutMixLazy
          items={remote}
          periodDays={periodDays}
          sampleSize={facetBody?.sample_size ?? null}
          title={t("remoteMixTitle")}
        />
        <DonutMixLazy
          items={contract}
          periodDays={periodDays}
          sampleSize={facetBody?.sample_size ?? null}
          title={t("contractMixTitle")}
        />
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <RankBarsLazy
          items={techRank}
          periodDays={periodDays}
          sampleSize={techSampleSize}
          title={tExec("topTechnologies")}
          valueLabel={t("colMentions")}
          onBarClick={(tech) => {
            router.push(
              `/relations?view=graph&seed=${encodeURIComponent(tech)}`,
            );
          }}
        />
        <RankBarsLazy
          items={langItems}
          periodDays={periodDays}
          sampleSize={langBody?.sample_size ?? null}
          title={t("langRankTitle")}
        />
      </div>
      {certRank.length > 0 ? (
        <RankBarsLazy
          items={certRank}
          periodDays={periodDays}
          sampleSize={certBody?.sample_size ?? null}
          title={tExec("topCertifications")}
          valueLabel={t("colMentions")}
        />
      ) : null}
    </div>
  );
}

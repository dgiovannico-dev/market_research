"use client";

import { useTranslations } from "next-intl";
import type { MarketSeriesPayload } from "@/lib/api";
import { MultiSeriesChartLazy } from "@/shared/ui/charts";

export type RelationsSeriesPanelProps = {
  periodDays: number;
  techSeries: MarketSeriesPayload | null;
  countrySeries: MarketSeriesPayload | null;
  ratesSeries: MarketSeriesPayload | null;
};

export function RelationsSeriesPanel({
  periodDays,
  techSeries,
  countrySeries,
  ratesSeries,
}: RelationsSeriesPanelProps) {
  const t = useTranslations("relations");
  const tCharts = useTranslations("charts");
  const emptySeries = t("emptySeries");
  const bucketLabel = t("axisBucket");

  return (
    <div
      id="relations-panel-series"
      role="tabpanel"
      aria-labelledby="relations-tab-series"
      className="space-y-5"
    >
      <section className="space-y-2">
        <h3 className="text-sm font-semibold tracking-tight text-[var(--ink)]">
          {t("sectionTechSeries")}
        </h3>
        <MultiSeriesChartLazy
          series={techSeries?.series ?? []}
          periodDays={techSeries?.period_days ?? periodDays}
          sampleSize={techSeries?.sample_size ?? null}
          title={t("seriesTechTitle")}
          emptyMessage={emptySeries}
          xAxisLabel={bucketLabel}
          yAxisLabel={tCharts("axisJobs")}
          guideRepresents={t("guideSeriesTech")}
          guideHowToRead={t("guideSeriesTechRead")}
        />
      </section>

      <section className="space-y-2">
        <h3 className="text-sm font-semibold tracking-tight text-[var(--ink)]">
          {t("sectionCountrySeries")}
        </h3>
        <MultiSeriesChartLazy
          series={countrySeries?.series ?? []}
          periodDays={countrySeries?.period_days ?? periodDays}
          sampleSize={countrySeries?.sample_size ?? null}
          title={t("seriesCountryTitle")}
          emptyMessage={emptySeries}
          xAxisLabel={bucketLabel}
          yAxisLabel={tCharts("axisJobs")}
          guideRepresents={t("guideSeriesCountry")}
          guideHowToRead={t("guideSeriesCountryRead")}
        />
      </section>

      <section className="space-y-2">
        <h3 className="text-sm font-semibold tracking-tight text-[var(--ink)]">
          {t("sectionRatesSeries")}
        </h3>
        <MultiSeriesChartLazy
          series={ratesSeries?.series ?? []}
          periodDays={ratesSeries?.period_days ?? periodDays}
          sampleSize={ratesSeries?.sample_size ?? null}
          title={t("seriesRatesTitle")}
          emptyMessage={emptySeries}
          xAxisLabel={bucketLabel}
          yAxisLabel={tCharts("axisMedian")}
          guideRepresents={t("guideSeriesRates")}
          guideHowToRead={t("guideSeriesRatesRead")}
        />
      </section>
    </div>
  );
}

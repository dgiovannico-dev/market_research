"use client";

import { useTranslations } from "next-intl";
import type { LanguageCountryMatrix, TechCountryMatrix } from "@/lib/api";
import type { HeatTriplet } from "./cooccurrenceHeat";
import { RelationsHeatSection } from "./RelationsHeatSection";

export type RelationsPlaceHeatPanelProps = {
  periodDays: number;
  matrix: TechCountryMatrix | null;
  countryHeatValues: HeatTriplet[];
  langMatrix: LanguageCountryMatrix | null;
  langCountryHeatValues: HeatTriplet[];
};

export function RelationsPlaceHeatPanel({
  periodDays,
  matrix,
  countryHeatValues,
  langMatrix,
  langCountryHeatValues,
}: RelationsPlaceHeatPanelProps) {
  const t = useTranslations("relations");
  const tCharts = useTranslations("charts");
  const emptyHeat = t("emptyHeat");
  const jobsLabel = tCharts("colJobs");

  return (
    <div
      id="relations-heat-panel-place"
      role="tabpanel"
      aria-labelledby="relations-heat-tab-place"
      className="space-y-5"
    >
      <RelationsHeatSection
        sectionTitle={t("sectionTechCountry")}
        xLabels={matrix?.countries ?? []}
        yLabels={matrix?.technologies ?? []}
        values={countryHeatValues}
        periodDays={matrix?.period_days ?? periodDays}
        sampleSize={matrix?.sample_size ?? null}
        title={t("heatTechCountryTitle")}
        emptyMessage={emptyHeat}
        xAxisLabel={tCharts("axisCountry")}
        yAxisLabel={tCharts("axisTechnology")}
        valueLabel={jobsLabel}
        guideRepresents={t("guideHeatTechCountry")}
        guideHowToRead={t("guideHeatTechCountryRead")}
      />

      <RelationsHeatSection
        sectionTitle={t("sectionLangCountry")}
        xLabels={langMatrix?.countries ?? []}
        yLabels={langMatrix?.languages ?? []}
        values={langCountryHeatValues}
        periodDays={langMatrix?.period_days ?? periodDays}
        sampleSize={langMatrix?.sample_size ?? null}
        title={t("heatLangCountryTitle")}
        emptyMessage={emptyHeat}
        xAxisLabel={tCharts("axisCountry")}
        yAxisLabel={tCharts("axisLanguage")}
        valueLabel={jobsLabel}
        guideRepresents={t("guideHeatLangCountry")}
        guideHowToRead={t("guideHeatLangCountryRead")}
      />
    </div>
  );
}

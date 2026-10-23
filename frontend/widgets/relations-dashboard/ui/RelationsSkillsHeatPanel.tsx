"use client";

import { useTranslations } from "next-intl";
import type { RoleTechMatrix, SeniorityTechMatrix } from "@/lib/api";
import type { HeatTriplet } from "./cooccurrenceHeat";
import { RelationsHeatSection } from "./RelationsHeatSection";

export type RelationsSkillsHeatPanelProps = {
  periodDays: number;
  techHeat: { labels: string[]; values: HeatTriplet[] };
  coocJobsAnalyzed: number | null;
  roleTech: RoleTechMatrix | null;
  roleTechHeatValues: HeatTriplet[];
  seniorityTech: SeniorityTechMatrix | null;
  seniorityTechHeatValues: HeatTriplet[];
};

export function RelationsSkillsHeatPanel({
  periodDays,
  techHeat,
  coocJobsAnalyzed,
  roleTech,
  roleTechHeatValues,
  seniorityTech,
  seniorityTechHeatValues,
}: RelationsSkillsHeatPanelProps) {
  const t = useTranslations("relations");
  const tCharts = useTranslations("charts");
  const emptyHeat = t("emptyHeat");
  const jobsLabel = tCharts("colJobs");

  return (
    <div
      id="relations-heat-panel-skills"
      role="tabpanel"
      aria-labelledby="relations-heat-tab-skills"
      className="space-y-5"
    >
      <RelationsHeatSection
        sectionTitle={t("sectionTechTech")}
        xLabels={techHeat.labels}
        yLabels={techHeat.labels}
        values={techHeat.values}
        periodDays={periodDays}
        sampleSize={coocJobsAnalyzed}
        title={t("heatTechTechTitle")}
        emptyMessage={emptyHeat}
        xAxisLabel={tCharts("axisTechnology")}
        yAxisLabel={tCharts("axisTechnology")}
        valueLabel={t("colSupport")}
        guideRepresents={t("guideHeatTechTech")}
        guideHowToRead={t("guideHeatTechTechRead")}
      />

      <RelationsHeatSection
        sectionTitle={t("sectionRoleTech")}
        xLabels={roleTech?.technologies ?? []}
        yLabels={roleTech?.role_families ?? []}
        values={roleTechHeatValues}
        periodDays={roleTech?.period_days ?? periodDays}
        sampleSize={roleTech?.sample_size ?? null}
        title={t("heatRoleTechTitle")}
        emptyMessage={emptyHeat}
        xAxisLabel={tCharts("axisTechnology")}
        yAxisLabel={tCharts("axisRoleFamily")}
        valueLabel={jobsLabel}
        guideRepresents={t("guideHeatRoleTech")}
        guideHowToRead={t("guideHeatRoleTechRead")}
      />

      <RelationsHeatSection
        sectionTitle={t("sectionSeniorityTech")}
        xLabels={seniorityTech?.technologies ?? []}
        yLabels={seniorityTech?.seniorities ?? []}
        values={seniorityTechHeatValues}
        periodDays={seniorityTech?.period_days ?? periodDays}
        sampleSize={seniorityTech?.sample_size ?? null}
        title={t("heatSeniorityTechTitle")}
        emptyMessage={emptyHeat}
        xAxisLabel={tCharts("axisTechnology")}
        yAxisLabel={tCharts("axisSeniority")}
        valueLabel={jobsLabel}
        guideRepresents={t("guideHeatSeniorityTech")}
        guideHowToRead={t("guideHeatSeniorityTechRead")}
      />
    </div>
  );
}

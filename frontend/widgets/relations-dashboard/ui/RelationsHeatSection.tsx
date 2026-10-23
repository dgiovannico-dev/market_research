"use client";

import { HeatMatrixLazy } from "@/shared/ui/charts";
import type { HeatTriplet } from "./cooccurrenceHeat";

type RelationsHeatSectionProps = {
  sectionTitle: string;
  xLabels: string[];
  yLabels: string[];
  values: HeatTriplet[];
  periodDays: number;
  sampleSize: number | null;
  title: string;
  emptyMessage: string;
  xAxisLabel: string;
  yAxisLabel: string;
  valueLabel: string;
  guideRepresents: string;
  guideHowToRead: string;
};

export function RelationsHeatSection({
  sectionTitle,
  xLabels,
  yLabels,
  values,
  periodDays,
  sampleSize,
  title,
  emptyMessage,
  xAxisLabel,
  yAxisLabel,
  valueLabel,
  guideRepresents,
  guideHowToRead,
}: RelationsHeatSectionProps) {
  return (
    <section className="space-y-2">
      <h3 className="text-sm font-semibold tracking-tight text-[var(--ink)]">
        {sectionTitle}
      </h3>
      <HeatMatrixLazy
        xLabels={xLabels}
        yLabels={yLabels}
        values={values}
        periodDays={periodDays}
        sampleSize={sampleSize}
        title={title}
        emptyMessage={emptyMessage}
        xAxisLabel={xAxisLabel}
        yAxisLabel={yAxisLabel}
        valueLabel={valueLabel}
        showTopN={false}
        guideRepresents={guideRepresents}
        guideHowToRead={guideHowToRead}
      />
    </section>
  );
}

"use client";

import { startTransition, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { usePathname, useRouter } from "@/i18n/navigation";
import type {
  LanguageCountryMatrix,
  RoleTechMatrix,
  SeniorityTechMatrix,
  TechCountryMatrix,
} from "@/lib/api";
import type { HeatTriplet } from "./cooccurrenceHeat";
import {
  RelationsHeatGroupTabs,
  type RelationsHeatGroup,
} from "./RelationsHeatGroupTabs";
import { RelationsPlaceHeatPanel } from "./RelationsPlaceHeatPanel";
import { RelationsSkillsHeatPanel } from "./RelationsSkillsHeatPanel";

export type RelationsHeatmapsPanelProps = {
  periodDays: number;
  techHeat: { labels: string[]; values: HeatTriplet[] };
  coocJobsAnalyzed: number | null;
  matrix: TechCountryMatrix | null;
  countryHeatValues: HeatTriplet[];
  langMatrix: LanguageCountryMatrix | null;
  langCountryHeatValues: HeatTriplet[];
  roleTech: RoleTechMatrix | null;
  roleTechHeatValues: HeatTriplet[];
  seniorityTech: SeniorityTechMatrix | null;
  seniorityTechHeatValues: HeatTriplet[];
};

const DEFAULT_HEAT_GROUP: RelationsHeatGroup = "skills";

function parseHeatGroup(raw: string | null): RelationsHeatGroup {
  return raw === "place" ? "place" : DEFAULT_HEAT_GROUP;
}

function writeHeatGroupToUrl(
  pathname: string,
  searchParams: URLSearchParams,
  router: ReturnType<typeof useRouter>,
  next: RelationsHeatGroup,
) {
  const params = new URLSearchParams(searchParams.toString());
  if (next === DEFAULT_HEAT_GROUP) params.delete("heat");
  else params.set("heat", next);
  const qs = params.toString();
  startTransition(() => {
    router.replace(qs ? `${pathname}?${qs}` : pathname, { scroll: false });
  });
}

/**
 * Heatmaps panel: Skills / Place group tabs + one heat panel.
 * Fetches stay in RelationsDashboard — this only swaps composition.
 */
export function RelationsHeatmapsPanel({
  periodDays,
  techHeat,
  coocJobsAnalyzed,
  matrix,
  countryHeatValues,
  langMatrix,
  langCountryHeatValues,
  roleTech,
  roleTechHeatValues,
  seniorityTech,
  seniorityTechHeatValues,
}: RelationsHeatmapsPanelProps) {
  const searchParams = useSearchParams();
  const pathname = usePathname();
  const router = useRouter();

  const heatFromUrl = parseHeatGroup(searchParams.get("heat"));
  const [heatGroup, setHeatGroupState] =
    useState<RelationsHeatGroup>(heatFromUrl);

  useEffect(() => {
    setHeatGroupState(heatFromUrl);
  }, [heatFromUrl]);

  const setHeatGroup = (next: RelationsHeatGroup) => {
    setHeatGroupState(next);
    writeHeatGroupToUrl(pathname, searchParams, router, next);
  };

  return (
    <div
      id="relations-panel-heat"
      role="tabpanel"
      aria-labelledby="relations-tab-heat"
      className="space-y-4"
    >
      <RelationsHeatGroupTabs value={heatGroup} onChange={setHeatGroup} />

      {heatGroup === "skills" ? (
        <RelationsSkillsHeatPanel
          periodDays={periodDays}
          techHeat={techHeat}
          coocJobsAnalyzed={coocJobsAnalyzed}
          roleTech={roleTech}
          roleTechHeatValues={roleTechHeatValues}
          seniorityTech={seniorityTech}
          seniorityTechHeatValues={seniorityTechHeatValues}
        />
      ) : (
        <RelationsPlaceHeatPanel
          periodDays={periodDays}
          matrix={matrix}
          countryHeatValues={countryHeatValues}
          langMatrix={langMatrix}
          langCountryHeatValues={langCountryHeatValues}
        />
      )}
    </div>
  );
}

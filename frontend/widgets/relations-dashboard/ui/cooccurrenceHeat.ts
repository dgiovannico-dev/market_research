/** Build a square tech×tech heat matrix from co-occurrence pairs (top-N by support). */

export type CooccurrencePairLike = {
  tech_a: string;
  tech_b: string;
  support: number;
};

export type HeatTriplet = [xIndex: number, yIndex: number, value: number];

export function buildCooccurrenceHeat(
  pairs: CooccurrencePairLike[],
  topN: number,
): { labels: string[]; values: HeatTriplet[] } {
  const weight = new Map<string, number>();
  for (const p of pairs) {
    const a = String(p.tech_a);
    const b = String(p.tech_b);
    const support = Number(p.support) || 0;
    if (!a || !b || support <= 0) continue;
    weight.set(a, (weight.get(a) ?? 0) + support);
    weight.set(b, (weight.get(b) ?? 0) + support);
  }

  const labels = [...weight.entries()]
    .sort((x, y) => y[1] - x[1] || x[0].localeCompare(y[0]))
    .slice(0, Math.max(0, topN))
    .map(([name]) => name);

  const index = new Map(labels.map((name, i) => [name, i]));
  const cell = new Map<string, number>();
  for (const p of pairs) {
    const i = index.get(String(p.tech_a));
    const j = index.get(String(p.tech_b));
    if (i == null || j == null) continue;
    const support = Number(p.support) || 0;
    cell.set(`${i},${j}`, support);
    cell.set(`${j},${i}`, support);
  }

  const values: HeatTriplet[] = [];
  for (const [key, support] of cell) {
    const [xi, yi] = key.split(",").map(Number);
    values.push([xi, yi, support]);
  }
  return { labels, values };
}

export function techCountryCellsToHeat(
  technologies: string[],
  countries: string[],
  cells: { technology: string; country_code: string; jobs: number }[],
): HeatTriplet[] {
  const xIndex = new Map(countries.map((c, i) => [c, i]));
  const yIndex = new Map(technologies.map((t, i) => [t, i]));
  const values: HeatTriplet[] = [];
  for (const cell of cells) {
    const xi = xIndex.get(cell.country_code);
    const yi = yIndex.get(cell.technology);
    if (xi == null || yi == null) continue;
    values.push([xi, yi, cell.jobs]);
  }
  return values;
}

/** Same layout as tech×country: x=countries, y=languages. */
export function languageCountryCellsToHeat(
  languages: string[],
  countries: string[],
  cells: { language: string; country_code: string; jobs: number }[],
): HeatTriplet[] {
  return techCountryCellsToHeat(
    languages,
    countries,
    cells.map((c) => ({
      technology: c.language,
      country_code: c.country_code,
      jobs: c.jobs,
    })),
  );
}

/** Role×tech heat: x=technologies, y=role_families. */
export function roleTechCellsToHeat(
  roleFamilies: string[],
  technologies: string[],
  cells: { role_family: string; technology: string; jobs: number }[],
): HeatTriplet[] {
  const xIndex = new Map(technologies.map((t, i) => [t, i]));
  const yIndex = new Map(roleFamilies.map((r, i) => [r, i]));
  const values: HeatTriplet[] = [];
  for (const cell of cells) {
    const xi = xIndex.get(cell.technology);
    const yi = yIndex.get(cell.role_family);
    if (xi == null || yi == null) continue;
    values.push([xi, yi, cell.jobs]);
  }
  return values;
}

/** Seniority×tech heat: x=technologies, y=seniorities. */
export function seniorityTechCellsToHeat(
  seniorities: string[],
  technologies: string[],
  cells: { seniority: string; technology: string; jobs: number }[],
): HeatTriplet[] {
  const xIndex = new Map(technologies.map((t, i) => [t, i]));
  const yIndex = new Map(seniorities.map((s, i) => [s, i]));
  const values: HeatTriplet[] = [];
  for (const cell of cells) {
    const xi = xIndex.get(cell.technology);
    const yi = yIndex.get(cell.seniority);
    if (xi == null || yi == null) continue;
    values.push([xi, yi, cell.jobs]);
  }
  return values;
}

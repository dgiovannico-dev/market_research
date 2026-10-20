import Link from "next/link";
import { api } from "@/lib/api";

function formatKpi(value: number, unit: string) {
  if (unit === "percent") return `${value.toFixed(1)}%`;
  return new Intl.NumberFormat("en").format(value);
}

export default async function ExecutivePage() {
  let summary = null as Awaited<ReturnType<typeof api.summary>> | null;
  let error: string | null = null;
  try {
    summary = await api.summary(30);
  } catch (e) {
    error = e instanceof Error ? e.message : "Failed to load dashboard";
  }

  if (error || !summary) {
    return (
      <div className="card p-6">
        <h2 className="text-lg font-semibold">API offline or empty</h2>
        <p className="mt-2 text-sm opacity-80">{error}</p>
        <p className="mt-4 text-sm">
          Start backend with Docker Compose, then open Sources to collect Remotive/Arbeitnow or import
          CSV.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <section className="card p-5">
        <p className="text-sm opacity-70">Last {summary.period_days} days · {summary.generated_at}</p>
        <p className="mt-2 text-sm">{summary.disclaimer}</p>
        <p className="mt-2 text-xs uppercase tracking-wide text-amber-700">
          Growth status: {summary.growth_status}
        </p>
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {summary.kpis.map((kpi) => (
          <article key={kpi.metric_name} className="card p-4">
            <p className="text-xs uppercase tracking-wide opacity-60">{kpi.metric_name}</p>
            <p className="mt-2 text-3xl font-semibold">{formatKpi(kpi.metric_value, kpi.unit)}</p>
            <p className="mt-2 text-sm opacity-80">{kpi.definition}</p>
            <div className="mt-3 flex flex-wrap gap-2">
              <span className="badge">n={kpi.sample_size}</span>
              <span className="badge">{kpi.evidence_kind}</span>
            </div>
            <p className="mt-3 text-xs opacity-60">Limits: {kpi.limits}</p>
          </article>
        ))}
      </section>

      <section className="grid gap-4 md:grid-cols-2">
        <article className="card p-4">
          <h2 className="font-semibold">Top technologies (observed mentions)</h2>
          <ul className="mt-3 space-y-2 text-sm">
            {summary.top_technologies.map((t) => (
              <li key={t.technology} className="flex justify-between border-b border-[var(--line)] py-1">
                <Link href={`/explorer?technology=${encodeURIComponent(t.technology)}`}>
                  {t.technology}
                </Link>
                <span>{t.job_skill_mentions}</span>
              </li>
            ))}
          </ul>
        </article>
        <article className="card p-4">
          <h2 className="font-semibold">Top countries (observed jobs)</h2>
          <ul className="mt-3 space-y-2 text-sm">
            {summary.top_countries.map((c) => (
              <li key={c.country_code} className="flex justify-between border-b border-[var(--line)] py-1">
                <span>{c.country_code}</span>
                <span>{c.jobs}</span>
              </li>
            ))}
          </ul>
          <p className="mt-4 text-xs opacity-60">
            Sources enabled: {summary.data_quality.sources_enabled}/
            {summary.data_quality.sources_total}. Last success:{" "}
            {summary.data_quality.last_source_success_at ?? "never"}
          </p>
        </article>
      </section>
    </div>
  );
}

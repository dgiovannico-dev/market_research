import Link from "next/link";
import { api } from "@/lib/api";

export default async function ExplorerPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | undefined>>;
}) {
  const sp = await searchParams;
  const params = new URLSearchParams();
  if (sp.technology) params.set("technology", sp.technology);
  if (sp.country_code) params.set("country_code", sp.country_code);
  params.set("limit", "50");

  const [summary, jobs] = await Promise.all([
    api.summary(90).catch(() => null),
    api.jobs(params.toString()).catch(() => ({ total: 0, items: [] })),
  ]);

  return (
    <div className="space-y-4">
      <section className="card p-4">
        <h2 className="text-lg font-semibold">Market Explorer</h2>
        <p className="text-sm opacity-70">
          Drill from observed KPI slices into concrete job records. Filters affect backend queries.
        </p>
        <form method="get" className="mt-3 flex flex-wrap gap-2">
          <input
            name="technology"
            defaultValue={sp.technology}
            placeholder="Technology"
            className="rounded border px-3 py-2"
          />
          <input
            name="country_code"
            defaultValue={sp.country_code}
            placeholder="Country"
            className="rounded border px-3 py-2"
          />
          <button className="rounded bg-teal-700 px-3 py-2 text-white">Filter</button>
        </form>
      </section>

      {summary && (
        <section className="grid gap-3 md:grid-cols-4">
          {summary.kpis.slice(0, 4).map((k) => (
            <div key={k.metric_name} className="card p-3 text-sm">
              <div className="opacity-60">{k.metric_name}</div>
              <div className="text-2xl font-semibold">{k.metric_value}</div>
              <div className="text-xs">n={k.sample_size}</div>
            </div>
          ))}
        </section>
      )}

      <section className="card p-4">
        <h3 className="font-semibold">Matching jobs ({jobs.total})</h3>
        <ul className="mt-3 space-y-2 text-sm">
          {jobs.items.map((j) => (
            <li key={j.id} className="flex justify-between gap-4 border-b border-[var(--line)] py-2">
              <div>
                <div className="font-medium">{j.title}</div>
                <div className="text-xs opacity-60">
                  {j.company} · {j.country_code} · {j.contract_type}/{j.remote_type}
                </div>
              </div>
              <Link href={j.canonical_url} className="text-teal-700 underline" target="_blank">
                source
              </Link>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}

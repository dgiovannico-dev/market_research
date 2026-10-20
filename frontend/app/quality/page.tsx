import { api } from "@/lib/api";

export default async function QualityPage() {
  let quality: Record<string, unknown> | null = null;
  let error: string | null = null;
  try {
    quality = await api.quality();
  } catch (e) {
    error = e instanceof Error ? e.message : "Failed";
  }

  const metrics = (quality?.metrics || {}) as Record<string, number>;
  const sources = (quality?.sources || []) as Array<Record<string, unknown>>;

  return (
    <div className="space-y-4">
      <section className="card p-4">
        <h2 className="text-lg font-semibold">Data Quality</h2>
        <p className="text-sm opacity-70">
          {(quality?.disclaimer as string) ||
            "Quality describes this database coverage, not the external market."}
        </p>
        <p className="mt-2 text-sm">
          Canonical jobs: <strong>{String(quality?.total_canonical_jobs ?? 0)}</strong>
        </p>
      </section>
      {error && <div className="card p-4 text-sm text-red-700">{error}</div>}
      <section className="grid gap-3 md:grid-cols-3">
        {Object.entries(metrics).map(([k, v]) => (
          <div key={k} className="card p-4">
            <div className="text-xs uppercase opacity-60">{k}</div>
            <div className="mt-2 text-2xl font-semibold">{v}</div>
          </div>
        ))}
      </section>
      <section className="card overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead className="border-b border-[var(--line)] text-xs uppercase opacity-70">
            <tr>
              <th className="px-3 py-2 text-left">Source</th>
              <th className="px-3 py-2 text-left">Status</th>
              <th className="px-3 py-2 text-left">Enabled</th>
              <th className="px-3 py-2 text-left">Last success</th>
              <th className="px-3 py-2 text-left">Notes</th>
            </tr>
          </thead>
          <tbody>
            {sources.map((s) => (
              <tr key={String(s.id)} className="border-b border-[var(--line)] align-top">
                <td className="px-3 py-2">{String(s.name)}</td>
                <td className="px-3 py-2">{String(s.connector_status)}</td>
                <td className="px-3 py-2">{String(s.enabled)}</td>
                <td className="px-3 py-2">{String(s.last_success_at ?? "—")}</td>
                <td className="px-3 py-2 text-xs opacity-70">{String(s.coverage_notes ?? "")}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}

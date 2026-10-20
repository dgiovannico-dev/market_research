import { api } from "@/lib/api";

export default async function TrendsPage() {
  let trends = { items: [] as Record<string, unknown>[] };
  let error: string | null = null;
  try {
    trends = await api.trends(90);
  } catch (e) {
    error = e instanceof Error ? e.message : "Failed";
  }

  return (
    <div className="space-y-4">
      <section className="card p-4">
        <h2 className="text-lg font-semibold">Technology Trends</h2>
        <p className="text-sm opacity-70">
          Half-period comparison of observed skill mentions. Growth is marked insufficient_data when
          previous window sample is zero or support is below threshold.
        </p>
      </section>
      {error && <div className="card p-4 text-sm text-red-700">{error}</div>}
      <section className="card overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead className="border-b border-[var(--line)] text-xs uppercase opacity-70">
            <tr>
              <th className="px-3 py-2 text-left">Technology</th>
              <th className="px-3 py-2 text-left">Category</th>
              <th className="px-3 py-2 text-right">Recent</th>
              <th className="px-3 py-2 text-right">Previous</th>
              <th className="px-3 py-2 text-right">Growth %</th>
              <th className="px-3 py-2 text-left">Status</th>
            </tr>
          </thead>
          <tbody>
            {trends.items.map((item) => (
              <tr key={String(item.technology)} className="border-b border-[var(--line)]">
                <td className="px-3 py-2">{String(item.technology)}</td>
                <td className="px-3 py-2">{String(item.category)}</td>
                <td className="px-3 py-2 text-right">{String(item.recent_mentions)}</td>
                <td className="px-3 py-2 text-right">{String(item.previous_mentions)}</td>
                <td className="px-3 py-2 text-right">
                  {item.growth_pct == null ? "—" : Number(item.growth_pct).toFixed(1)}
                </td>
                <td className="px-3 py-2">{String(item.status)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}

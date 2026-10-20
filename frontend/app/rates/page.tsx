async function fetchRates() {
  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const res = await fetch(`${API_URL}/api/v1/market/rates?days=180&min_sample=3`, { cache: "no-store" });
  if (!res.ok) throw new Error(`rates failed: ${res.status}`);
  return res.json();
}

export default async function RatesPage() {
  let data: { items?: Record<string, unknown>[]; disclaimer?: string; jobs_with_rates?: number } = {};
  let error: string | null = null;
  try {
    data = await fetchRates();
  } catch (e) {
    error = e instanceof Error ? e.message : "Failed";
  }

  return (
    <div className="space-y-4">
      <section className="card p-4">
        <h2 className="text-lg font-semibold">Rate Explorer</h2>
        <p className="text-sm opacity-70">{data.disclaimer}</p>
        <p className="mt-2 text-sm">Jobs with advertised rates: {String(data.jobs_with_rates ?? 0)}</p>
      </section>
      {error && <div className="card p-4 text-sm text-red-700">{error}</div>}
      <section className="card overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead className="border-b border-[var(--line)] text-xs uppercase opacity-70">
            <tr>
              <th className="px-3 py-2 text-left">Country</th>
              <th className="px-3 py-2 text-left">Currency</th>
              <th className="px-3 py-2 text-left">Unit</th>
              <th className="px-3 py-2 text-right">n</th>
              <th className="px-3 py-2 text-right">Median</th>
              <th className="px-3 py-2 text-right">P25</th>
              <th className="px-3 py-2 text-right">P75</th>
              <th className="px-3 py-2 text-left">Status</th>
            </tr>
          </thead>
          <tbody>
            {(data.items || []).map((row, idx) => (
              <tr key={idx} className="border-b border-[var(--line)]">
                <td className="px-3 py-2">{String(row.country_code)}</td>
                <td className="px-3 py-2">{String(row.currency)}</td>
                <td className="px-3 py-2">{String(row.unit)}</td>
                <td className="px-3 py-2 text-right">{String(row.sample_size)}</td>
                <td className="px-3 py-2 text-right">
                  {row.median == null ? "—" : Number(row.median).toFixed(1)}
                </td>
                <td className="px-3 py-2 text-right">
                  {row.p25 == null ? "—" : Number(row.p25).toFixed(1)}
                </td>
                <td className="px-3 py-2 text-right">
                  {row.p75 == null ? "—" : Number(row.p75).toFixed(1)}
                </td>
                <td className="px-3 py-2">{String(row.status)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}

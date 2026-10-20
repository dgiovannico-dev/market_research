async function fetchCountries() {
  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const res = await fetch(`${API_URL}/api/v1/market/countries?days=90`, { cache: "no-store" });
  if (!res.ok) throw new Error(`countries failed: ${res.status}`);
  return res.json();
}

export default async function CountriesPage() {
  let data: { items?: Record<string, unknown>[]; disclaimer?: string } = {};
  let error: string | null = null;
  try {
    data = await fetchCountries();
  } catch (e) {
    error = e instanceof Error ? e.message : "Failed";
  }

  return (
    <div className="space-y-4">
      <section className="card p-4">
        <h2 className="text-lg font-semibold">Country Comparison</h2>
        <p className="text-sm opacity-70">{data.disclaimer}</p>
        <p className="mt-2 text-xs text-amber-700">Not legal/tax advice. Remote ≠ Italian-resident access.</p>
      </section>
      {error && <div className="card p-4 text-sm text-red-700">{error}</div>}
      <section className="grid gap-3 md:grid-cols-2">
        {(data.items || []).map((c) => (
          <article key={String(c.country_code)} className="card p-4 text-sm">
            <h3 className="text-lg font-semibold">{String(c.country_code)}</h3>
            <p>Jobs observed: {String(c.jobs_observed)}</p>
            <p>Remote share: {(Number(c.remote_share) * 100).toFixed(1)}%</p>
            <p>B2B/freelance share: {(Number(c.b2b_freelance_share) * 100).toFixed(1)}%</p>
            <p>
              Residence explicitly allowed/restricted: {String(c.explicitly_allowed_residence)}/
              {String(c.explicitly_restricted_residence)}
            </p>
            <p className="mt-2 text-xs opacity-70">
              Top tech:{" "}
              {((c.top_technologies as Array<{ name: string; mentions: number }>) || [])
                .map((t) => `${t.name}(${t.mentions})`)
                .join(", ")}
            </p>
          </article>
        ))}
      </section>
    </div>
  );
}

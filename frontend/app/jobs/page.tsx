import { api } from "@/lib/api";

export default async function JobsPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | undefined>>;
}) {
  const sp = await searchParams;
  const params = new URLSearchParams();
  if (sp.q) params.set("q", sp.q);
  if (sp.country_code) params.set("country_code", sp.country_code);
  if (sp.contract_type) params.set("contract_type", sp.contract_type);
  if (sp.remote_type) params.set("remote_type", sp.remote_type);
  if (sp.technology) params.set("technology", sp.technology);
  params.set("limit", "100");

  let data = { total: 0, items: [] as Awaited<ReturnType<typeof api.jobs>>["items"] };
  let error: string | null = null;
  try {
    data = await api.jobs(params.toString());
  } catch (e) {
    error = e instanceof Error ? e.message : "Failed";
  }

  return (
    <div className="space-y-4">
      <section className="card p-4">
        <h2 className="text-lg font-semibold">Job Explorer</h2>
        <p className="text-sm opacity-70">
          Server-side filters over persisted jobs. Evidence kinds shown per classification field.
        </p>
        <form method="get" className="mt-4 grid gap-2 md:grid-cols-5">
          <input name="q" defaultValue={sp.q} placeholder="Search" className="rounded border px-3 py-2" />
          <input
            name="country_code"
            defaultValue={sp.country_code}
            placeholder="Country (IT/CH/DE…)"
            className="rounded border px-3 py-2"
          />
          <input
            name="contract_type"
            defaultValue={sp.contract_type}
            placeholder="Contract"
            className="rounded border px-3 py-2"
          />
          <input
            name="remote_type"
            defaultValue={sp.remote_type}
            placeholder="Remote type"
            className="rounded border px-3 py-2"
          />
          <input
            name="technology"
            defaultValue={sp.technology}
            placeholder="Technology"
            className="rounded border px-3 py-2"
          />
          <button className="rounded bg-teal-700 px-3 py-2 text-white md:col-span-5">Apply filters</button>
        </form>
      </section>

      {error && <div className="card p-4 text-sm text-red-700">{error}</div>}

      <section className="card overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="border-b border-[var(--line)] text-xs uppercase opacity-70">
            <tr>
              <th className="px-3 py-2">Title</th>
              <th className="px-3 py-2">Source</th>
              <th className="px-3 py-2">Country</th>
              <th className="px-3 py-2">Contract</th>
              <th className="px-3 py-2">Remote</th>
              <th className="px-3 py-2">Tech</th>
              <th className="px-3 py-2">Rate</th>
              <th className="px-3 py-2">URL</th>
            </tr>
          </thead>
          <tbody>
            {data.items.map((job) => (
              <tr key={job.id} className="border-b border-[var(--line)] align-top">
                <td className="px-3 py-2">
                  <div className="font-medium">{job.title}</div>
                  <div className="text-xs opacity-60">{job.company}</div>
                </td>
                <td className="px-3 py-2">{job.source}</td>
                <td className="px-3 py-2">{job.country_code}</td>
                <td className="px-3 py-2">
                  {job.contract_type}
                  <div className="text-xs opacity-60">{job.contract_evidence_kind}</div>
                </td>
                <td className="px-3 py-2">{job.remote_type}</td>
                <td className="px-3 py-2">
                  {job.technologies.slice(0, 5).map((t) => t.name).join(", ")}
                </td>
                <td className="px-3 py-2">
                  {job.rates[0]
                    ? `${job.rates[0].amount_min ?? "?"}–${job.rates[0].amount_max ?? "?"} ${job.rates[0].currency ?? ""}/${job.rates[0].unit}`
                    : "NULL"}
                </td>
                <td className="px-3 py-2">
                  <a className="text-teal-700 underline" href={job.canonical_url} target="_blank" rel="noreferrer">
                    open
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <p className="px-3 py-2 text-xs opacity-60">Total matching: {data.total}</p>
      </section>
    </div>
  );
}

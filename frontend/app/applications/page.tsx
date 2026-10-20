import { ApplicationForm } from "@/components/ApplicationForm";

async function fetchApps() {
  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const res = await fetch(`${API_URL}/api/v1/applications`, { cache: "no-store" });
  if (!res.ok) throw new Error(`applications failed: ${res.status}`);
  return res.json();
}

export default async function ApplicationsPage() {
  let data: { items?: Record<string, unknown>[]; summary?: Record<string, unknown> } = {};
  let error: string | null = null;
  try {
    data = await fetchApps();
  } catch (e) {
    error = e instanceof Error ? e.message : "Failed";
  }
  const metrics = (data.summary?.metrics || {}) as Record<string, unknown>;

  return (
    <div className="space-y-4">
      <section className="card p-4">
        <h2 className="text-lg font-semibold">Applications & Outcomes</h2>
        <p className="text-sm opacity-70">Personal pipeline metrics — not market metrics.</p>
        {error && <p className="text-sm text-red-700">{error}</p>}
        <div className="mt-3 grid gap-2 md:grid-cols-4 text-sm">
          <div className="card p-3">Apps: {String(data.summary?.applications ?? 0)}</div>
          <div className="card p-3">Response: {String(metrics.response_rate ?? "—")}</div>
          <div className="card p-3">Interview: {String(metrics.interview_rate ?? "—")}</div>
          <div className="card p-3">Offer: {String(metrics.offer_rate ?? "—")}</div>
        </div>
      </section>
      <ApplicationForm />
      <section className="card overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead className="border-b border-[var(--line)] text-xs uppercase opacity-70">
            <tr>
              <th className="px-3 py-2 text-left">Date</th>
              <th className="px-3 py-2 text-left">Job</th>
              <th className="px-3 py-2 text-left">Channel</th>
              <th className="px-3 py-2 text-left">Response</th>
              <th className="px-3 py-2 text-left">Outcome</th>
            </tr>
          </thead>
          <tbody>
            {(data.items || []).map((row) => (
              <tr key={String(row.id)} className="border-b border-[var(--line)]">
                <td className="px-3 py-2">{String(row.applied_at)}</td>
                <td className="px-3 py-2">{String(row.job_id ?? "—")}</td>
                <td className="px-3 py-2">{String(row.channel ?? "—")}</td>
                <td className="px-3 py-2">{String(row.response ?? "—")}</td>
                <td className="px-3 py-2">{String(row.outcome ?? "—")}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}

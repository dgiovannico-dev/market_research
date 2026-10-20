import { EvaluateAlertsButton } from "@/components/EvaluateAlertsButton";

async function fetchAlerts() {
  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const res = await fetch(`${API_URL}/api/v1/alerts`, { cache: "no-store" });
  if (!res.ok) throw new Error(`alerts failed: ${res.status}`);
  return res.json();
}

export default async function AlertsPage() {
  let data: { items?: Record<string, unknown>[] } = { items: [] };
  let error: string | null = null;
  try {
    data = await fetchAlerts();
  } catch (e) {
    error = e instanceof Error ? e.message : "Failed";
  }

  return (
    <div className="space-y-4">
      <section className="card flex flex-wrap items-center justify-between gap-3 p-4">
        <div>
          <h2 className="text-lg font-semibold">Alerts</h2>
          <p className="text-sm opacity-70">Rules show evidence that triggered them.</p>
        </div>
        <EvaluateAlertsButton />
      </section>
      {error && <div className="card p-4 text-sm text-red-700">{error}</div>}
      {(data.items || []).map((a) => (
        <article key={String(a.id)} className="card p-4 text-sm">
          <h3 className="font-semibold">{String(a.name)}</h3>
          <p className="text-xs opacity-60">{String(a.rule_type)}</p>
          <p className="mt-2">Last triggered: {String(a.last_triggered_at ?? "never")}</p>
          <p className="mt-1 text-xs opacity-70">Evidence: {String(a.last_evidence ?? "—")}</p>
        </article>
      ))}
    </div>
  );
}

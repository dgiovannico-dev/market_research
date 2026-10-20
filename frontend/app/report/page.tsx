async function fetchReport() {
  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const res = await fetch(`${API_URL}/api/v1/reports/weekly`, { cache: "no-store" });
  if (!res.ok) throw new Error(`report failed: ${res.status}`);
  return res.json();
}

export default async function ReportPage() {
  let data: { markdown?: string; llm_health?: Record<string, unknown> } = {};
  let error: string | null = null;
  try {
    data = await fetchReport();
  } catch (e) {
    error = e instanceof Error ? e.message : "Failed";
  }

  return (
    <div className="space-y-4">
      <section className="card p-4">
        <h2 className="text-lg font-semibold">Weekly report</h2>
        <p className="text-sm opacity-70">
          Built from structured backend KPIs. LLM narrative only if provider healthy; otherwise
          deterministic Markdown.
        </p>
        <p className="mt-2 text-xs">
          LLM: {String(data.llm_health?.provider ?? "n/a")} healthy={String(data.llm_health?.healthy)}
        </p>
      </section>
      {error && <div className="card p-4 text-sm text-red-700">{error}</div>}
      <section className="card p-4">
        <pre className="whitespace-pre-wrap font-mono text-xs leading-relaxed">{data.markdown || ""}</pre>
      </section>
    </div>
  );
}

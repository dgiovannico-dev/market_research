import { api } from "@/lib/api";
import { LlmOpsButtons } from "@/components/LlmOpsButtons";
import { RunSourceButton } from "@/components/RunSourceButton";

export default async function SourcesPage() {
  const [sources, llm] = await Promise.all([
    api.sources().catch(() => ({ items: [] })),
    api.llmStatus().catch(() => ({ healthy: false, provider: "unknown" } as Record<string, unknown>)),
  ]);

  const provider = String(llm.provider ?? llm.configured_provider ?? "unknown");
  const healthy = String(llm.healthy ?? false);
  const mode = String(llm.classification_mode ?? "n/a");

  return (
    <div className="space-y-4">
      <section className="card p-4">
        <h2 className="text-lg font-semibold">Sources & LLM Control</h2>
        <p className="text-sm opacity-70">
          Only authorized/public connectors are runnable. Unsupported sources stay explicit.
        </p>
        <div className="mt-3 text-sm">
          LLM provider: <strong>{provider}</strong> · healthy: <strong>{healthy}</strong> · mode:{" "}
          <strong>{mode}</strong>
        </div>
        <LlmOpsButtons />
      </section>

      <section className="grid gap-3">
        {sources.items.map((s) => (
          <article key={String(s.id)} className="card p-4">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <h3 className="font-semibold">{String(s.name)}</h3>
                <p className="text-xs opacity-60">
                  {String(s.connector_type)} · {String(s.connector_status)} · enabled={String(s.enabled)}
                </p>
                <p className="mt-2 text-sm opacity-80">{String(s.coverage_notes ?? "")}</p>
              </div>
              {s.connector_status === "enabled" ? (
                <RunSourceButton sourceId={Number(s.id)} />
              ) : (
                <span className="badge">not runnable</span>
              )}
            </div>
          </article>
        ))}
      </section>
    </div>
  );
}

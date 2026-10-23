import { getTranslations, setRequestLocale } from "next-intl/server";
import { api } from "@/lib/api";
import { CredentialedConnectors } from "@/widgets/credentialed-connectors";
import { LlmOpsButtons } from "@/features/ops-llm";
import { RunFreeSourcesButton } from "@/features/run-free-sources";
import {
  CatalogBrowser,
  RunnableConnectorsPanel,
  type RunnableSource,
} from "@/widgets/sources-catalog";

type SourceItem = Record<string, unknown>;

function hasInsertEvidence(s: SourceItem): boolean {
  if (typeof s.has_insert_evidence === "boolean") return s.has_insert_evidence;
  return Number(s.insert_runs_count ?? 0) > 0;
}

function toRunnable(s: SourceItem): RunnableSource {
  return {
    id: Number(s.id),
    name: String(s.name ?? ""),
    connector_type: String(s.connector_type ?? ""),
    category: s.category != null ? String(s.category) : undefined,
    coverage_notes: s.coverage_notes != null ? String(s.coverage_notes) : undefined,
    verification_status:
      s.verification_status != null ? String(s.verification_status) : undefined,
    is_credentialed_scaffold: Boolean(s.is_credentialed_scaffold),
    has_insert_evidence:
      typeof s.has_insert_evidence === "boolean" ? s.has_insert_evidence : undefined,
    insert_runs_count:
      s.insert_runs_count != null ? Number(s.insert_runs_count) : undefined,
    last_insert_at: s.last_insert_at ? String(s.last_insert_at) : null,
    last_success_at: s.last_success_at ? String(s.last_success_at) : null,
    last_error: s.last_error ? String(s.last_error) : null,
  };
}

export default async function SourcesPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("sources");

  const [sources, llm, catalog] = await Promise.all([
    api.sources().catch(() => ({ items: [] as SourceItem[] })),
    api.llmStatus().catch(() => ({ healthy: false, provider: "unknown" } as Record<string, unknown>)),
    api.catalogSummary().catch(() => null),
  ]);

  const provider = String(llm.provider ?? llm.configured_provider ?? "unknown");
  const healthy = String(llm.healthy ?? false);
  const mode = String(llm.classification_mode ?? "n/a");
  const runnable = sources.items.filter((s) => s.connector_status === "enabled");
  const active = runnable.filter((s) => String(s.verification_status ?? "") === "ACTIVE");
  const activeWithoutInserts = active.filter((s) => !hasInsertEvidence(s)).length;

  return (
    <div className="space-y-4">
      <section className="card p-4">
        <h2 className="text-lg font-semibold">{t("title")}</h2>
        <p className="text-sm opacity-70">{t("subtitle")}</p>
        <div className="mt-3 text-sm">
          {t("llmLine", { provider, healthy, mode })}
        </div>
        {catalog ? (
          <div className="mt-3 text-sm opacity-80">
            {t("catalogLine", {
              total: catalog.total,
              keys: (catalog.active_connector_keys || []).join(", ") || "—",
            })}
            <div className="mt-1 text-xs opacity-60">
              {Object.entries(catalog.by_status || {})
                .map(([k, v]) => `${k}=${v}`)
                .join(" · ")}
            </div>
          </div>
        ) : null}
        {active.length > 0 ? (
          <p className="mt-3 text-sm">
            {activeWithoutInserts > 0 ? (
              <span className="cool-text font-medium">
                {t("activeNeedRun", { count: activeWithoutInserts, total: active.length })}
              </span>
            ) : (
              <span className="rise-text font-medium">
                {t("activeAllHaveInserts", { total: active.length })}
              </span>
            )}
          </p>
        ) : null}
        <LlmOpsButtons />
        <RunFreeSourcesButton
          sources={runnable.map((s) => ({
            id: Number(s.id),
            name: String(s.name ?? ""),
            connector_type: String(s.connector_type ?? ""),
            is_credentialed_scaffold: Boolean(s.is_credentialed_scaffold),
          }))}
        />
        <CredentialedConnectors />
      </section>

      {runnable.length === 0 ? (
        <section className="space-y-3">
          <h3 className="font-semibold">{t("runnableHeading")}</h3>
          <div className="card p-6 text-sm opacity-80">
            <p className="font-medium">{t("emptyRunnableTitle")}</p>
            <p className="mt-1 text-xs opacity-70">{t("emptyRunnableBody")}</p>
          </div>
        </section>
      ) : (
        <RunnableConnectorsPanel sources={runnable.map(toRunnable)} />
      )}

      <CatalogBrowser />
    </div>
  );
}

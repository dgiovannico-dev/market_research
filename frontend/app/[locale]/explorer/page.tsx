import { Suspense } from "react";
import { getTranslations, setRequestLocale } from "next-intl/server";
import {
  ExplorerJobList,
  ExplorerRefresh,
  ExplorerResultsState,
  ExplorerSearchForm,
  type ExplorerJob,
} from "@/widgets/explorer";
import { api, type DashboardLens } from "@/lib/api";
import type { ResearchIntent } from "@/entities/research-intent";

function parseLens(raw: string | undefined): DashboardLens {
  if (raw === "focus" || raw === "compare" || raw === "market") return raw;
  return "market";
}

function parseQueryId(raw: string | undefined): number | undefined {
  if (!raw) return undefined;
  const n = Number(raw);
  return Number.isFinite(n) && n > 0 ? Math.trunc(n) : undefined;
}

/** Prefer chrome `query_ids`; accept legacy singular `query_id`. */
function parseQueryIdFromSearch(sp: Record<string, string | undefined>): number | undefined {
  const first = (sp.query_ids || "").split(",")[0]?.trim();
  const fromIds = parseQueryId(first);
  if (fromIds != null) return fromIds;
  return parseQueryId(sp.query_id);
}

function asExplorerJobs(items: unknown[]): ExplorerJob[] {
  return items.flatMap((raw) => {
    if (!raw || typeof raw !== "object") return [];
    const j = raw as Record<string, unknown>;
    if (typeof j.id !== "number" || typeof j.title !== "string") return [];
    if (typeof j.canonical_url !== "string") return [];
    return [
      {
        id: j.id,
        title: j.title,
        company: typeof j.company === "string" ? j.company : null,
        country_code: typeof j.country_code === "string" ? j.country_code : "",
        contract_type: typeof j.contract_type === "string" ? j.contract_type : "",
        remote_type: typeof j.remote_type === "string" ? j.remote_type : "",
        canonical_url: j.canonical_url,
      },
    ];
  });
}

export default async function ExplorerPage({
  params,
  searchParams,
}: {
  params: Promise<{ locale: string }>;
  searchParams: Promise<Record<string, string | undefined>>;
}) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("explorer");
  const sp = await searchParams;

  // Accept legacy `technology` as q alias; never default to a profession string.
  const q = (sp.q || sp.technology || "").trim() || undefined;
  // Prefer chrome multi-select `countries=`; fall back to single country_code/country.
  const country =
    (sp.countries || sp.country_code || sp.country || "").trim().toUpperCase() ||
    undefined;
  const lens = parseLens(sp.lens);
  const queryId = parseQueryIdFromSearch(sp);

  const [jobsOutcome, intentsRes] = await Promise.all([
    api
      .researchJobs({ q, lens, query_id: queryId, country_code: country, limit: 50 })
      .then((data) => ({ ok: true as const, data }))
      .catch((err: unknown) => ({
        ok: false as const,
        message: err instanceof Error ? err.message : t("loadFailed"),
      })),
    api.listResearchIntents().catch(() => ({ items: [] as ResearchIntent[], total: 0 })),
  ]);

  const jobsRes = jobsOutcome.ok ? jobsOutcome.data : { total: 0, items: [] as unknown[] };
  const jobsError = jobsOutcome.ok ? null : jobsOutcome.message;
  const items = asExplorerJobs(jobsRes.items ?? []);
  const intents = intentsRes.items ?? [];

  return (
    <div className="space-y-4">
      <section className="card space-y-3 p-4">
        <div>
          <h2 className="font-display text-2xl font-semibold tracking-tight text-[var(--ink)]">
            {t("title")}
          </h2>
          <p className="mt-1 max-w-2xl text-sm text-[var(--muted)]">{t("subtitle")}</p>
        </div>

        <Suspense fallback={null}>
          <ExplorerSearchForm
            q={q}
            country={country}
            lens={lens}
            queryId={queryId}
            intents={intents}
          />
        </Suspense>

        <ExplorerRefresh
          key={queryId ?? "any"}
          intents={intents}
          preferredIntentId={queryId ?? null}
        />
      </section>

      {jobsError ? (
        <ExplorerResultsState
          mode="error"
          title={t("loadFailed")}
          body={jobsError}
          retryLabel={t("loadFailedHint")}
          openScan={t("openScan")}
          openFocus={t("openFocus")}
        />
      ) : items.length === 0 ? (
        <ExplorerResultsState
          mode="empty"
          title={t("jobsFound", { count: jobsRes.total ?? 0 })}
          body={t("empty")}
          hint={t("emptyHint")}
          openScan={t("openScan")}
          openFocus={t("openFocus")}
        />
      ) : (
        <ExplorerJobList total={jobsRes.total ?? 0} items={items} />
      )}
    </div>
  );
}

import { getTranslations } from "next-intl/server";
import { getJSON } from "@/shared/api";

type WeeklyReport = {
  markdown?: string;
  llm_health?: Record<string, unknown>;
};

async function fetchReport() {
  return getJSON<WeeklyReport>("/api/v1/reports/weekly");
}

export default async function ReportPage() {
  const t = await getTranslations("report");
  let data: WeeklyReport = {};
  let error: string | null = null;
  try {
    data = await fetchReport();
  } catch (e) {
    error = e instanceof Error ? e.message : t("loadFailed");
  }

  return (
    <div className="space-y-5">
      <header className="space-y-1">
        <h2 className="font-display text-2xl font-semibold tracking-tight text-[var(--ink)]">
          {t("title")}
        </h2>
        <p className="max-w-2xl text-sm text-[var(--muted)]">{t("subtitle")}</p>
        <p className="text-xs text-[var(--muted)]" style={{ fontFamily: "var(--mono)" }}>
          {t("llmLine", {
            provider: String(data.llm_health?.provider ?? "n/a"),
            healthy: String(data.llm_health?.healthy),
          })}
        </p>
      </header>
      {error ? (
        <div className="card p-4 text-sm text-red-700" role="alert">
          {error}
        </div>
      ) : null}
      <section className="card p-4">
        <pre
          className="whitespace-pre-wrap text-xs leading-relaxed text-[var(--ink)]"
          style={{ fontFamily: "var(--mono)" }}
        >
          {data.markdown || ""}
        </pre>
      </section>
    </div>
  );
}

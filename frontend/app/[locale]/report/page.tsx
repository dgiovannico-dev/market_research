import { getTranslations, setRequestLocale } from "next-intl/server";
import { getJSON } from "@/shared/api";
import { Markdown } from "@/shared/ui";

type WeeklyReport = {
  markdown?: string;
  llm_health?: Record<string, unknown>;
};

async function fetchReport(locale: string) {
  const q = locale ? `?locale=${encodeURIComponent(locale)}` : "";
  return getJSON<WeeklyReport>(`/api/v1/reports/weekly${q}`);
}

export default async function ReportPage({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("report");
  let data: WeeklyReport = {};
  let error: string | null = null;
  try {
    data = await fetchReport(locale);
  } catch (e) {
    error = e instanceof Error ? e.message : t("loadFailed");
  }

  const markdown = (data.markdown || "").trim();

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
      <section className="card p-5 sm:p-6" aria-label={t("title")}>
        {markdown ? (
          <Markdown>{markdown}</Markdown>
        ) : !error ? (
          <p className="text-sm text-[var(--muted)]">{t("empty")}</p>
        ) : null}
      </section>
    </div>
  );
}

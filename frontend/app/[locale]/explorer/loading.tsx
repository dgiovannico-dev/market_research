import { getTranslations } from "next-intl/server";

export default async function ExplorerLoading() {
  const t = await getTranslations("explorer");
  return (
    <div className="space-y-4" aria-busy="true" aria-live="polite">
      <section className="card space-y-3 p-4">
        <div className="h-5 w-32 rounded bg-[var(--line)] opacity-40" />
        <div className="h-10 w-full max-w-xl rounded bg-[var(--line)] opacity-30" />
        <p className="text-sm opacity-70">{t("loading")}</p>
      </section>
      <section className="card p-4 text-sm opacity-70">{t("loadingResults")}</section>
    </div>
  );
}

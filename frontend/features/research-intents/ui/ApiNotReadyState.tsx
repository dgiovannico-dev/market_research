"use client";

import { useTranslations } from "next-intl";

export function ApiNotReadyState() {
  const t = useTranslations("research");

  return (
    <section className="card space-y-2 p-6" role="status">
      <h2 className="font-display text-lg font-semibold tracking-tight text-[var(--ink)]">
        {t("apiNotReadyTitle")}
      </h2>
      <p className="text-sm text-[var(--muted)]">{t("apiNotReadyBody")}</p>
    </section>
  );
}

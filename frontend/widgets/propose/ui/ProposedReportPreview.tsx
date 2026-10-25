"use client";

import { useEffect, useState } from "react";
import { useLocale, useTranslations } from "next-intl";
import { assistantApi } from "@/entities/assistant";
import type { AssistantLocale } from "@/entities/assistant";

type Props = {
  prompt: string;
  title?: string;
  periodDays?: number;
};

export function ProposedReportPreview({ prompt, title, periodDays }: Props) {
  const t = useTranslations("assistant");
  const locale = useLocale() as AssistantLocale;
  const [objectUrl, setObjectUrl] = useState<string | null>(null);
  const [filename, setFilename] = useState("fmi-report.pdf");
  const [busy, setBusy] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    let createdUrl: string | null = null;
    setBusy(true);
    setError(null);
    setObjectUrl((prev) => {
      if (prev) URL.revokeObjectURL(prev);
      return null;
    });

    assistantApi
      .reportPdf({ prompt, locale })
      .then(({ blob, filename: name }) => {
        if (cancelled) return;
        createdUrl = URL.createObjectURL(blob);
        setObjectUrl(createdUrl);
        if (name) setFilename(name);
        setBusy(false);
      })
      .catch((e: unknown) => {
        if (cancelled) return;
        setError(e instanceof Error ? e.message : t("reportPdfFailed"));
        setBusy(false);
      });

    return () => {
      cancelled = true;
      if (createdUrl) URL.revokeObjectURL(createdUrl);
    };
  }, [prompt, locale, t]);

  const subtitleParts = [
    title,
    periodDays != null ? t("periodDays", { days: periodDays }) : null,
  ].filter(Boolean);

  return (
    <section className="card space-y-4 p-5" aria-label={t("reportPreviewAria")}>
      <header className="flex flex-wrap items-end justify-between gap-3">
        <div className="space-y-1">
          <h3 className="font-display text-base font-semibold tracking-tight text-[var(--ink)]">
            {t("reportPreviewTitle")}
          </h3>
          {subtitleParts.length > 0 ? (
            <p className="text-sm text-[var(--muted)]">{subtitleParts.join(" · ")}</p>
          ) : null}
        </div>
        {objectUrl ? (
          <a
            href={objectUrl}
            download={filename}
            className="rounded-md bg-[var(--signal)] px-3 py-1.5 text-sm font-medium text-white transition-opacity hover:opacity-90"
          >
            {t("reportPdfDownload")}
          </a>
        ) : null}
      </header>

      {busy ? <p className="text-sm text-[var(--muted)]">{t("reportPdfLoading")}</p> : null}
      {error ? <p className="text-sm text-[var(--warn)]">{error}</p> : null}

      {objectUrl && !busy ? (
        <div className="overflow-hidden rounded-lg border border-[var(--line)] bg-[var(--card)]">
          <iframe
            title={t("reportPreviewAria")}
            src={objectUrl}
            className="h-[min(70vh,720px)] w-full"
          />
        </div>
      ) : null}
    </section>
  );
}

"use client";

import { useTranslations } from "next-intl";

/** Distinguishes free public collectors from env-key scaffolds (Atlas badge tones). */
export function ConnectorKindBadge({
  credentialed,
}: {
  credentialed: boolean;
}) {
  const t = useTranslations("sources");
  if (credentialed) {
    return (
      <span className="badge cool-text" title={t("kindCredHint")}>
        {t("kindCredentialed")}
      </span>
    );
  }
  return (
    <span className="badge rise-text" title={t("kindFreeHint")}>
      {t("kindFreePublic")}
    </span>
  );
}

"use client";

import { useTranslations } from "next-intl";

type Props = {
  busy?: boolean;
  onSync: () => void;
};

export function IntentSyncButton({ busy, onSync }: Props) {
  const t = useTranslations("research");

  return (
    <button
      type="button"
      disabled={busy}
      className="rounded-full border border-[var(--line)] px-3 py-1.5 text-xs hover:border-[var(--signal)] disabled:opacity-50"
      onClick={onSync}
    >
      {busy ? t("syncing") : t("syncOne")}
    </button>
  );
}

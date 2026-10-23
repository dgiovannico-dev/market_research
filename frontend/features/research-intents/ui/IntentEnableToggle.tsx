"use client";

import { useTranslations } from "next-intl";

type Props = {
  enabled: boolean;
  busy?: boolean;
  onChange: (next: boolean) => void;
};

export function IntentEnableToggle({ enabled, busy, onChange }: Props) {
  const t = useTranslations("research");

  return (
    <label className="inline-flex items-center gap-2 text-sm">
      <input
        type="checkbox"
        className="size-4 accent-[var(--signal)]"
        checked={enabled}
        disabled={busy}
        onChange={(e) => onChange(e.target.checked)}
      />
      <span className="text-[var(--muted)]">{enabled ? t("enabled") : t("disabled")}</span>
    </label>
  );
}

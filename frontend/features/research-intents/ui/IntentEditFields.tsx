"use client";

import { useTranslations } from "next-intl";

type Props = {
  name: string;
  queryText: string;
  busy?: boolean;
  onNameChange: (value: string) => void;
  onQueryChange: (value: string) => void;
  onSave: () => void;
  onCancel: () => void;
};

export function IntentEditFields({
  name,
  queryText,
  busy,
  onNameChange,
  onQueryChange,
  onSave,
  onCancel,
}: Props) {
  const t = useTranslations("research");
  const tCommon = useTranslations("common");

  return (
    <div className="grid gap-2 sm:grid-cols-[1fr_2fr_auto_auto]">
      <label className="block text-xs text-[var(--muted)]">
        {t("labelField")}
        <input
          className="mt-1 w-full rounded border border-[var(--line)] bg-transparent px-2 py-1.5 text-sm text-[var(--ink)]"
          value={name}
          disabled={busy}
          onChange={(e) => onNameChange(e.target.value)}
        />
      </label>
      <label className="block text-xs text-[var(--muted)]">
        {t("queryField")}
        <input
          className="mt-1 w-full rounded border border-[var(--line)] bg-transparent px-2 py-1.5 text-sm text-[var(--ink)]"
          style={{ fontFamily: "var(--mono)" }}
          value={queryText}
          disabled={busy}
          onChange={(e) => onQueryChange(e.target.value)}
        />
      </label>
      <button
        type="button"
        disabled={busy || !name.trim() || !queryText.trim()}
        className="self-end rounded-full bg-[var(--signal)] px-3 py-1.5 text-xs text-white disabled:opacity-50"
        onClick={onSave}
      >
        {tCommon("save")}
      </button>
      <button
        type="button"
        disabled={busy}
        className="self-end rounded-full border border-[var(--line)] px-3 py-1.5 text-xs disabled:opacity-50"
        onClick={onCancel}
      >
        {tCommon("cancel")}
      </button>
    </div>
  );
}

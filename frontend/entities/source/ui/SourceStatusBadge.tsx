/** Verification-status pill for Sources / catalog / ops panels. */

const TONE: Record<string, string> = {
  ACTIVE: "rise-text",
  NEEDS_CREDENTIALS: "cool-text",
  UNDER_REVIEW: "signal-text",
  VALIDATED: "signal-text",
  REJECTED: "opacity-70",
};

export function statusToneClass(status: string): string {
  return TONE[status] ?? "";
}

export function SourceStatusBadge({
  status,
  label,
  title,
}: {
  status: string;
  label?: string;
  title?: string;
}) {
  const key = status.trim() || "—";
  const tone = statusToneClass(key);
  return (
    <span className={`badge ${tone}`.trim()} title={title}>
      {label ?? key}
    </span>
  );
}

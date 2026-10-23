import { Link } from "@/i18n/navigation";

type Props = {
  mode: "empty" | "error";
  title: string;
  body: string;
  hint?: string;
  openScan: string;
  openFocus: string;
  retryLabel?: string;
};

/** Shared empty / error card for Explore results. */
export function ExplorerResultsState({
  mode,
  title,
  body,
  hint,
  openScan,
  openFocus,
  retryLabel,
}: Props) {
  return (
    <section
      className="card space-y-2 p-4 text-sm"
      role={mode === "error" ? "alert" : "status"}
    >
      <h3
        className={`font-display font-semibold tracking-tight ${
          mode === "error" ? "text-[var(--warn)]" : "text-[var(--ink)]"
        }`}
      >
        {title}
      </h3>
      <p className={mode === "error" ? "text-[var(--warn)]" : "text-[var(--muted)]"}>{body}</p>
      {hint ? (
        <p className="text-[var(--muted)]">
          {hint}{" "}
          <Link href="/market-scan" className="underline signal-text">
            {openScan}
          </Link>{" "}
          /{" "}
          <Link href="/focus" className="underline signal-text">
            {openFocus}
          </Link>
        </p>
      ) : null}
      {mode === "error" && retryLabel ? (
        <p className="text-xs text-[var(--muted)]">{retryLabel}</p>
      ) : null}
    </section>
  );
}

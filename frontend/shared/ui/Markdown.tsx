import type { Components } from "react-markdown";
import ReactMarkdown from "react-markdown";

type Props = {
  children: string;
  className?: string;
};

const components: Components = {
  h1: ({ children }) => (
    <h1 className="font-display text-xl font-semibold tracking-tight text-[var(--ink)]">
      {children}
    </h1>
  ),
  h2: ({ children }) => (
    <h2 className="mt-6 font-display text-base font-semibold tracking-tight text-[var(--ink)] first:mt-0">
      {children}
    </h2>
  ),
  h3: ({ children }) => (
    <h3 className="mt-4 font-display text-sm font-semibold text-[var(--ink)]">{children}</h3>
  ),
  p: ({ children }) => (
    <p className="text-sm leading-relaxed text-[var(--ink)]">{children}</p>
  ),
  ul: ({ children }) => (
    <ul className="list-disc space-y-1.5 pl-5 text-sm leading-relaxed text-[var(--ink)]">
      {children}
    </ul>
  ),
  ol: ({ children }) => (
    <ol className="list-decimal space-y-1.5 pl-5 text-sm leading-relaxed text-[var(--ink)]">
      {children}
    </ol>
  ),
  li: ({ children }) => <li className="pl-0.5">{children}</li>,
  strong: ({ children }) => (
    <strong className="font-semibold text-[var(--ink)]">{children}</strong>
  ),
  em: ({ children }) => <em className="italic text-[var(--ink)]">{children}</em>,
  a: ({ href, children }) => (
    <a
      href={href}
      className="text-[var(--signal)] underline-offset-2 hover:underline"
      rel="noopener noreferrer"
      target="_blank"
    >
      {children}
    </a>
  ),
  code: ({ children }) => (
    <code
      className="rounded bg-[var(--card)] px-1 py-0.5 text-[0.85em] text-[var(--ink)]"
      style={{ fontFamily: "var(--mono)" }}
    >
      {children}
    </code>
  ),
  pre: ({ children }) => (
    <pre
      className="overflow-x-auto rounded-md border border-[var(--line)] bg-[var(--card)] p-3 text-xs leading-relaxed text-[var(--muted)]"
      style={{ fontFamily: "var(--mono)" }}
    >
      {children}
    </pre>
  ),
  hr: () => <hr className="border-[var(--line)]" />,
  blockquote: ({ children }) => (
    <blockquote className="border-l-2 border-[var(--line)] pl-3 text-sm italic text-[var(--muted)]">
      {children}
    </blockquote>
  ),
};

export function Markdown({ children, className }: Props) {
  const source = (children || "").trim();
  if (!source) return null;
  return (
    <div className={className ? `space-y-3 ${className}` : "space-y-3"}>
      <ReactMarkdown components={components}>{source}</ReactMarkdown>
    </div>
  );
}

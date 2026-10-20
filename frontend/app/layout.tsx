import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "Freelance Market Intelligence",
  description: "Evidence-first IT freelance market analytics",
};

const nav = [
  { href: "/", label: "Executive" },
  { href: "/explorer", label: "Explorer" },
  { href: "/trends", label: "Trends" },
  { href: "/skills", label: "Skills" },
  { href: "/rates", label: "Rates" },
  { href: "/countries", label: "Countries" },
  { href: "/jobs", label: "Jobs" },
  { href: "/profile", label: "Profile" },
  { href: "/applications", label: "Applications" },
  { href: "/quality", label: "Quality" },
  { href: "/alerts", label: "Alerts" },
  { href: "/report", label: "Report" },
  { href: "/sources", label: "Sources" },
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link
          href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        <div className="min-h-screen">
          <header className="border-b border-[var(--line)] bg-[color-mix(in_srgb,var(--card)_80%,transparent)]">
            <div className="mx-auto flex max-w-7xl flex-col gap-3 px-4 py-4 md:flex-row md:items-center md:justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.2em] text-teal-700 dark:text-teal-300">
                  Freelance Market Intelligence
                </p>
                <h1 className="text-xl font-semibold">Observed demand, not invented market size</h1>
              </div>
              <nav className="flex flex-wrap gap-2 text-sm">
                {nav.map((item) => (
                  <Link
                    key={item.href}
                    href={item.href}
                    className="rounded-full border border-[var(--line)] px-3 py-1.5 hover:border-teal-600"
                  >
                    {item.label}
                  </Link>
                ))}
              </nav>
            </div>
          </header>
          <main className="mx-auto max-w-7xl px-4 py-6">{children}</main>
        </div>
      </body>
    </html>
  );
}

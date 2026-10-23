import type { Metadata } from "next";
import { IBM_Plex_Mono, Source_Sans_3, Syne } from "next/font/google";
import { notFound } from "next/navigation";
import { hasLocale, NextIntlClientProvider } from "next-intl";
import { getMessages, setRequestLocale } from "next-intl/server";
import { DashboardPrefsProvider } from "@/features/dashboard-prefs";
import { CountryFilterBoundary } from "@/features/country-filter";
import { AppChrome } from "@/widgets/app-chrome";
import { routing } from "@/i18n/routing";
import "../globals.css";

const fontDisplay = Syne({
  subsets: ["latin"],
  weight: ["600", "700"],
  variable: "--font-display",
  display: "swap",
});

const fontSans = Source_Sans_3({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-sans",
  display: "swap",
});

const fontMono = IBM_Plex_Mono({
  subsets: ["latin"],
  weight: ["400", "500"],
  variable: "--font-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Freelance Market Intelligence",
  description: "Evidence-first IT freelance market analytics",
};

export function generateStaticParams() {
  return routing.locales.map((locale) => ({ locale }));
}

type Props = {
  children: React.ReactNode;
  params: Promise<{ locale: string }>;
};

export default async function LocaleLayout({ children, params }: Props) {
  const { locale } = await params;
  if (!hasLocale(routing.locales, locale)) {
    notFound();
  }

  setRequestLocale(locale);
  const messages = await getMessages();

  return (
    <html
      lang={locale}
      suppressHydrationWarning
      className={`${fontDisplay.variable} ${fontSans.variable} ${fontMono.variable}`}
    >
      <body>
        <NextIntlClientProvider locale={locale} messages={messages}>
          <DashboardPrefsProvider>
            <CountryFilterBoundary>
              <AppChrome>{children}</AppChrome>
            </CountryFilterBoundary>
          </DashboardPrefsProvider>
        </NextIntlClientProvider>
      </body>
    </html>
  );
}

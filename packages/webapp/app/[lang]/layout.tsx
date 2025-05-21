import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { ThemeProvider } from "next-themes";

import QueryClientProvider from "@/providers/QueryClientProvider";
import { WebAppProvider } from "@/providers/WebAppProvider";
import { Language } from "@/i18n/conf";

import "../globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "TG WebApp scaffold",
  description: "Helps to build telegram web apps",
};

export async function generateStaticParams() {
  return ["en", "ru"].map((lang) => ({ lang }));
}

export default async function RootLayout({
  params,
  children,
}: Readonly<{
  params: Promise<{
    lang: Language;
  }>;
  children: React.ReactNode;
}>) {
  const { lang } = await params;

  return (
    <html lang={lang} suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <WebAppProvider>
          <QueryClientProvider>
            <ThemeProvider defaultTheme="lofi">{children}</ThemeProvider>
          </QueryClientProvider>
        </WebAppProvider>
      </body>
    </html>
  );
}

import type { Metadata } from "next";
import { ThemeProvider } from "@/components/layout/ThemeProvider";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "AI Trends - AI 뉴스 큐레이션",
    template: "%s | AI Trends",
  },
  description: "다양한 글로벌 소스의 AI 뉴스를 한국어로 한눈에",
  openGraph: {
    title: "AI Trends",
    description: "다양한 글로벌 소스의 AI 뉴스를 한국어로 한눈에",
    type: "website",
    locale: "ko_KR",
  },
  twitter: {
    card: "summary_large_image",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko" className="dark" suppressHydrationWarning>
      <head>
        {/* Prevent flash of wrong theme */}
        <script
          dangerouslySetInnerHTML={{
            __html: `
              try {
                const t = localStorage.getItem('theme');
                if (t === 'light') document.documentElement.classList.replace('dark', 'light');
                else if (t === 'system' && !window.matchMedia('(prefers-color-scheme: dark)').matches)
                  document.documentElement.classList.replace('dark', 'light');
              } catch {}
            `,
          }}
        />
      </head>
      <body className="min-h-screen flex flex-col antialiased">
        <ThemeProvider>
          <Header />
          <main className="flex-1">{children}</main>
          <Footer />
        </ThemeProvider>
      </body>
    </html>
  );
}

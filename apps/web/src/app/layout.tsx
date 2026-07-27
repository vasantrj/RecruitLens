import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";
import { Providers } from "./providers";
import { ConditionalNavbar } from "@/components/conditional-navbar";
import { PageLoader } from "@/components/page-loader";
import { ConditionalPageBackground } from "@/components/conditional-page-background";

const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  weight: "100 900",
});
const geistMono = localFont({
  src: "./fonts/GeistMonoVF.woff",
  variable: "--font-geist-mono",
  weight: "100 900",
});

export const metadata: Metadata = {
  title: "RecruitLens",
  description: "AI-powered resume screening and job matching",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
        style={{ background: "var(--paper)", color: "var(--ink)" }}
      >
        <Providers>
          <PageLoader />
          <ConditionalPageBackground />
          <ConditionalNavbar />
          {children}
        </Providers>
      </body>
    </html>
  );
}
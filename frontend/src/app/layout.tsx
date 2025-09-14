import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { MainLayout } from "@/components/layout/main-layout";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "LegalClarity AI - Make Legal Documents Understandable",
  description: "Analyze contracts, leases, and legal documents with AI-powered insights. Get risk assessments, plain-language explanations, and expert guidance for everyday legal decisions.",
  keywords: ["legal documents", "contract analysis", "AI legal assistant", "document review", "consumer protection"],
  authors: [{ name: "LegalClarity AI" }],
  openGraph: {
    title: "LegalClarity AI - Legal Document Analysis",
    description: "Make legal documents understandable with AI-powered analysis and expert insights.",
    type: "website",
    url: "https://legalclarity.ai",
  },
  twitter: {
    card: "summary_large_image",
    title: "LegalClarity AI",
    description: "AI-powered legal document analysis for everyone",
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full">
      <body className={`${inter.className} h-full antialiased`}>
        <MainLayout>{children}</MainLayout>
      </body>
    </html>
  );
}

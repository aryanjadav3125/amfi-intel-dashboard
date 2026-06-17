import type { Metadata } from "next";
import { Inter, Manrope, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import Link from "next/link";
import LiveHeader from "@/components/LiveHeader";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const manrope = Manrope({ subsets: ["latin"], variable: "--font-manrope" });
const jetbrainsMono = JetBrains_Mono({ subsets: ["latin"], variable: "--font-jetbrains-mono" });

export const metadata: Metadata = {
  title: "AMFI Intel Terminal",
  description: "Enterprise-grade analytics terminal for Indian Mutual Fund portfolios.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.variable} ${manrope.variable} ${jetbrainsMono.variable} font-sans min-h-screen text-slate-100 antialiased bg-[#050914] flex flex-col md:flex-row overflow-hidden`}>
        {/* Slim Professional Sidebar Navigation Panel */}
        <aside className="w-16 flex-col border-r border-slate-800/50 bg-[#0a0f1c] shrink-0 hidden md:flex z-20 shadow-2xl">
          {/* Brand Header */}
          <div className="h-14 flex items-center justify-center border-b border-slate-800/50">
            <div className="w-8 h-8 rounded bg-indigo-600 flex items-center justify-center font-bold text-white shadow shadow-indigo-500/20 text-xs tracking-tighter">
              AG
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="flex-1 py-4 flex flex-col gap-2 items-center">
            <Link 
              href="/" 
              title="Overview Dashboard"
              className="w-10 h-10 flex items-center justify-center rounded-lg text-slate-400 hover:text-white hover:bg-slate-800/50 transition-all"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2H6a2 2 0 01-2-2v-4zM14 16a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2h-2a2 2 0 01-2-2v-4z" />
              </svg>
            </Link>

            <Link 
              href="/funds" 
              title="Fund Screener"
              className="w-10 h-10 flex items-center justify-center rounded-lg text-slate-400 hover:text-white hover:bg-slate-800/50 transition-all"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </Link>

            <Link 
              href="/compare" 
              title="Comparison Matrix"
              className="w-10 h-10 flex items-center justify-center rounded-lg text-slate-400 hover:text-white hover:bg-slate-800/50 transition-all"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 002 2h2a2 2 0 002-2z" />
              </svg>
            </Link>

            <Link 
              href="/portfolio" 
              title="Portfolio Modeling"
              className="w-10 h-10 flex items-center justify-center rounded-lg text-slate-400 hover:text-white hover:bg-slate-800/50 transition-all"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
              </svg>
            </Link>

            <Link 
              href="/pipeline" 
              title="Data Ingestion Logs"
              className="w-10 h-10 flex items-center justify-center rounded-lg text-slate-400 hover:text-white hover:bg-slate-800/50 transition-all"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 4v5h.582m15.356 2A8.001 8.001 0 1121.21 8H17" />
              </svg>
            </Link>
          </nav>
        </aside>

        {/* Content Panel */}
        <main className="flex-1 min-w-0 flex flex-col h-screen overflow-hidden">
          {/* Top global header bar using Live Header */}
          <LiveHeader />
          
          {/* View Container */}
          <div className="flex-1 p-6 md:p-8 overflow-y-auto w-full mx-auto relative bg-[#0a0f1c]">
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-indigo-900/20 via-[#0a0f1c] to-[#0a0f1c] -z-10 pointer-events-none" />
            {children}
          </div>
        </main>
      </body>
    </html>
  );
}

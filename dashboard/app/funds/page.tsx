"use client";

import { useState } from "react";
import FundTable from "@/components/FundTable";
import ReportsPanel from "@/components/ReportsPanel";
import AumPanel from "@/components/AumPanel";

export default function FundsExplorerPage() {
  const [activeTab, setActiveTab] = useState<"latest-nav" | "reports" | "aum">("latest-nav");

  const tabs = [
    {
      id: "latest-nav",
      name: "Latest NAV Explorer",
      icon: (
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 10h16M4 14h16M4 18h16" />
        </svg>
      )
    },
    {
      id: "reports",
      name: "NAV Download & History",
      icon: (
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
        </svg>
      )
    },
    {
      id: "aum",
      name: "AUM Disclosures",
      icon: (
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 002 2h2a2 2 0 002-2z" />
        </svg>
      )
    }
  ] as const;

  return (
    <div className="space-y-6">
      {/* Top Heading */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-extrabold tracking-tight text-white">Mutual Fund Asset Explorer</h2>
          <p className="text-slate-400 text-sm mt-1">
            Perform queries across historical Indian mutual funds, filter by category class, and analyze performance CAGR records.
          </p>
        </div>
      </div>

      {/* Tab Selectors */}
      <div className="flex border-b border-slate-900 overflow-x-auto gap-2 scrollbar-none">
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-5 py-3 text-xs font-semibold uppercase tracking-wider transition-all border-b-2 outline-none shrink-0 ${
                isActive
                  ? "border-indigo-500 text-white bg-indigo-950/20"
                  : "border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-900/30"
              }`}
            >
              {tab.icon}
              {tab.name}
            </button>
          );
        })}
      </div>

      {/* Render Panel */}
      <div className="mt-6">
        {activeTab === "latest-nav" && <FundTable />}
        {activeTab === "reports" && <ReportsPanel />}
        {activeTab === "aum" && <AumPanel />}
      </div>
    </div>
  );
}


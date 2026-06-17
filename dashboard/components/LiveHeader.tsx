"use client";

import { useEffect, useState } from "react";
import useSWR from "swr";
import { fetchJson, PipelineStatus } from "@/lib/api";

export default function LiveHeader() {
  const [mounted, setMounted] = useState(false);
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    setMounted(true);
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const { data: pipeline } = useSWR<PipelineStatus>('/pipeline/status', fetchJson, { refreshInterval: 30000 });
  const isSyncing = pipeline?.status === "running";

  return (
    <header className="h-14 border-b border-slate-800/50 flex items-center justify-between px-6 bg-[#050914] z-10 shrink-0 shadow-sm">
      <div className="flex items-center gap-4">
        <h1 className="font-bold tracking-tight text-slate-200">AMFI Intel <span className="text-indigo-400 font-mono font-medium ml-1">Terminal</span></h1>
        <div className="h-4 w-[1px] bg-slate-800"></div>
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider">Env</span>
          <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-indigo-950/30 text-indigo-300 border border-indigo-900/50">PROD</span>
        </div>
      </div>
      
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2 text-xs font-mono text-slate-400">
          <span className={`w-2 h-2 rounded-full ${isSyncing ? "bg-amber-400 animate-pulse" : "bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]"}`}></span>
          {isSyncing ? "SYNCING DATA..." : "API CONNECTED"}
        </div>
        <div className="text-xs font-mono text-slate-300 font-medium tracking-wide min-w-[80px] text-right">
          {mounted ? `${time.toLocaleTimeString('en-US', { hour12: false })} UTC` : "--:--:-- UTC"}
        </div>
      </div>
    </header>
  );
}

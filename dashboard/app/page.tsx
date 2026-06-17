/**
 * Dashboard Overview Page
 * 
 * This is the root landing page for the terminal. It utilizes SWR to maintain
 * a live, real-time connection to the backend pipeline and analytics endpoints.
 * All structural metrics, performance tables, and distribution charts are rendered here.
 */
"use client";

import Link from "next/link";
import useSWR from "swr";
import { fetchJson, FundSummary, PipelineStatus, DashboardOverview } from "@/lib/api";
import { formatCurrency, formatPercentage } from "@/lib/utils";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, Cell } from "recharts";

const POLLING_INTERVAL = 15000; // 15 seconds real-time stream

export default function DashboardOverviewPage() {
  const { data: overview, isLoading: overviewLoading } = useSWR<DashboardOverview>('/dashboard/overview', fetchJson, { refreshInterval: POLLING_INTERVAL });
  const { data: catSum, isLoading: catLoading } = useSWR<Array<{ category: string; fund_count: number }>>('/categories/summary', fetchJson, { refreshInterval: POLLING_INTERVAL });
  const { data: pipeline, isLoading: pipeLoading } = useSWR<PipelineStatus>('/pipeline/status', fetchJson, { refreshInterval: POLLING_INTERVAL });
  const { data: fundsList, isLoading: fundsLoading } = useSWR<{funds: FundSummary[], total: number}>('/funds?limit=100', fetchJson, { refreshInterval: POLLING_INTERVAL });

  const loading = overviewLoading || catLoading || pipeLoading || fundsLoading;
  
  const categories = catSum ? catSum.slice(0, 5) : [];
  const leaders = fundsList?.funds 
    ? [...fundsList.funds].sort((a, b) => (b.cagr_1y ?? 0) - (a.cagr_1y ?? 0)).slice(0, 6)
    : [];

  return (
    <div className="space-y-6">
      {/* Terminal Title Bar */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4 border-b border-slate-800/50 pb-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-white uppercase flex items-center gap-2">
            <svg className="w-5 h-5 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 002 2h2a2 2 0 002-2z" />
            </svg>
            Market Overview
          </h2>
          <p className="text-slate-500 text-xs mt-1 font-mono">
            System streaming AMFI NAV records and compute indices.
          </p>
        </div>
        <div className="flex gap-3">
          <Link 
            href="/funds"
            className="bg-[#0f172a] border border-slate-700 hover:bg-slate-800 text-slate-300 text-xs font-mono px-4 py-2 rounded shadow-sm transition-all"
          >
            [ OPEN SCREENER ]
          </Link>
        </div>
      </div>

      {loading ? (
        <div className="h-64 flex items-center justify-center font-mono text-xs text-slate-500 animate-pulse">
          INITIALIZING TERMINAL BLOCKS...
        </div>
      ) : (
        <div className="space-y-6">
          {/* Dense Metric Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-[#0f172a]/80 border border-slate-800/80 p-4 rounded flex flex-col justify-between">
              <span className="text-[9px] uppercase font-bold tracking-widest text-slate-500 mb-2">Tracked Assets</span>
              <p className="text-2xl font-black text-slate-200 font-mono leading-none">{overview?.total_funds?.toLocaleString() || 0}</p>
            </div>
            <div className="bg-[#0f172a]/80 border border-slate-800/80 p-4 rounded flex flex-col justify-between">
              <span className="text-[9px] uppercase font-bold tracking-widest text-slate-500 mb-2">Fund Houses</span>
              <p className="text-2xl font-black text-slate-200 font-mono leading-none">{overview?.total_amcs?.toLocaleString() || 0}</p>
            </div>
            <div className="bg-[#0f172a]/80 border border-slate-800/80 p-4 rounded flex flex-col justify-between">
              <span className="text-[9px] uppercase font-bold tracking-widest text-slate-500 mb-2">Asset Classes</span>
              <p className="text-2xl font-black text-indigo-400 font-mono leading-none">{overview?.total_categories?.toLocaleString() || 0}</p>
            </div>
            <div className="bg-[#0f172a]/80 border border-slate-800/80 p-4 rounded flex flex-col justify-between">
              <span className="text-[9px] uppercase font-bold tracking-widest text-slate-500 mb-2">NAV Freshness</span>
              <p className="text-sm font-bold text-emerald-400 font-mono leading-none flex items-center gap-2 mt-2">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                {overview?.latest_nav_update || "N/A"}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Top Performance Table */}
            <div className="lg:col-span-2 bg-[#0f172a]/80 border border-slate-800/80 rounded flex flex-col overflow-hidden">
              <div className="px-4 py-3 border-b border-slate-800/50 flex justify-between items-center bg-[#0a0f1c]">
                <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">Top Yield Performers (1Y)</h3>
                <span className="text-[9px] text-slate-500 font-mono">LIVE FEED</span>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-[#0a0f1c]/50 text-[10px] uppercase font-mono tracking-wider text-slate-500 border-b border-slate-800/50">
                      <th className="px-4 py-2 font-medium">Scheme Identifier</th>
                      <th className="px-4 py-2 font-medium">Category</th>
                      <th className="px-4 py-2 font-medium text-right">Latest NAV</th>
                      <th className="px-4 py-2 font-medium text-right">1Y CAGR</th>
                    </tr>
                  </thead>
                  <tbody className="text-xs font-mono divide-y divide-slate-800/30">
                    {leaders.length === 0 ? (
                      <tr>
                        <td colSpan={4} className="px-4 py-8 text-center text-slate-600">NO DATA STREAM</td>
                      </tr>
                    ) : (
                      leaders.map((fund) => {
                        const isPositive = (fund.cagr_1y ?? 0) >= 0;
                        return (
                          <tr key={fund.scheme_id} className="hover:bg-slate-800/20 transition-colors group">
                            <td className="px-4 py-3">
                              <Link href={`/funds/${fund.scheme_id}`} className="text-indigo-300 font-sans font-semibold group-hover:text-indigo-200 block truncate max-w-[250px]">
                                {fund.scheme_name}
                              </Link>
                              <span className="text-[9px] text-slate-500">{fund.scheme_id}</span>
                            </td>
                            <td className="px-4 py-3 text-slate-400 text-[10px]">{fund.category}</td>
                            <td className="px-4 py-3 text-right font-bold text-slate-200">{formatCurrency(fund.latest_nav)}</td>
                            <td className="px-4 py-3 text-right">
                              <span className={`px-1.5 py-0.5 rounded ${isPositive ? "bg-emerald-950/40 text-emerald-400" : "bg-rose-950/40 text-rose-400"}`}>
                                {formatPercentage(fund.cagr_1y)}
                              </span>
                            </td>
                          </tr>
                        );
                      })
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Distributions Bar Chart */}
            <div className="bg-[#0f172a]/80 border border-slate-800/80 rounded flex flex-col overflow-hidden h-full min-h-[300px]">
              <div className="px-4 py-3 border-b border-slate-800/50 bg-[#0a0f1c]">
                <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">Asset Distribution</h3>
              </div>
              <div className="p-4 flex-1 flex flex-col justify-center">
                {categories.length === 0 ? (
                   <div className="text-center font-mono text-xs text-slate-600">NO DATA</div>
                ) : (
                  <div className="h-full w-full min-h-[220px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={categories} layout="vertical" margin={{ top: 0, right: 20, left: 0, bottom: 0 }}>
                        <XAxis type="number" hide />
                        <YAxis dataKey="category" type="category" stroke="#64748b" fontSize={9} tickLine={false} axisLine={false} width={80} tickFormatter={(val) => val.length > 12 ? val.substring(0, 12) + '...' : val} />
                        <Tooltip
                          cursor={{ fill: '#1e293b', opacity: 0.3 }}
                          contentStyle={{ backgroundColor: '#050914', borderColor: '#1e293b', borderRadius: '4px', fontSize: '10px', fontFamily: 'monospace' }}
                          itemStyle={{ color: '#818cf8', fontWeight: 'bold' }}
                        />
                        <Bar dataKey="fund_count" name="Schemes" radius={[0, 2, 2, 0]} barSize={20}>
                          {categories.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={index % 2 === 0 ? '#4f46e5' : '#6366f1'} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                )}
              </div>
            </div>
          </div>
          
          {/* System Logs */}
          <div className="bg-[#050914] border border-slate-800/80 rounded p-4 font-mono text-[10px]">
             <div className="flex justify-between items-center text-slate-500 mb-2 border-b border-slate-800/50 pb-2">
                <span>SYSTEM &gt; SCRAPER LOGS</span>
                <span>STATE: {pipeline?.status?.toUpperCase() || 'IDLE'}</span>
             </div>
             <div className="grid grid-cols-3 gap-4 text-slate-400">
                <div>[SYNC_TYPE]: {pipeline?.run_type || 'N/A'}</div>
                <div>[OMITTED]: {pipeline?.records_skipped || 0}</div>
                <div className={pipeline?.errors_count ? 'text-rose-400' : ''}>[ERRORS]: {pipeline?.errors_count || 0}</div>
             </div>
          </div>
        </div>
      )}
    </div>
  );
}

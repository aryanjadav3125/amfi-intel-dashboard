"use client";

import { useEffect, useState } from "react";
import { ResponsiveContainer, PieChart, Pie, Cell, Legend, Tooltip, BarChart, Bar, XAxis, YAxis } from "recharts";
import { getAumSummary, getCategoryAum, AumSummaryResponse, CategoryAumResponse } from "@/lib/api";

const COLORS = ["#6366f1", "#10b981", "#f59e0b", "#ec4899", "#8b5cf6", "#3b82f6", "#06b6d4"];

export default function AumPanel() {
  const [summary, setSummary] = useState<AumSummaryResponse | null>(null);
  const [categories, setCategories] = useState<CategoryAumResponse[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const [sumRes, catRes] = await Promise.all([
          getAumSummary(),
          getCategoryAum()
        ]);
        setSummary(sumRes);
        setCategories(catRes);
      } catch (err) {
        console.error("Failed to load AUM data:", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const formatCr = (value: number | null) => {
    if (value === null || value === undefined) return "N/A";
    return `₹${value.toLocaleString("en-IN", { maximumFractionDigits: 2 })} Cr`;
  };

  const formatFolios = (value: number | null) => {
    if (value === null || value === undefined) return "N/A";
    if (value >= 10000000) return `${(value / 10000000).toFixed(2)} Cr`;
    if (value >= 100000) return `${(value / 100000).toFixed(2)} L`;
    return value.toLocaleString("en-IN");
  };

  if (loading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {Array.from({ length: 3 }).map((_, idx) => (
            <div key={idx} className="h-28 bg-slate-900/60 border border-slate-800 rounded-xl" />
          ))}
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="h-80 bg-slate-900/60 border border-slate-800 rounded-xl" />
          <div className="h-80 bg-slate-900/60 border border-slate-800 rounded-xl" />
        </div>
      </div>
    );
  }

  if (!summary) {
    return (
      <div className="p-12 text-center text-slate-500 text-sm">
        Failed to load AUM metrics. Please seed database and check backend connectivity.
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Dynamic Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6">
        <div className="glass-card p-6 rounded-xl border border-slate-800/80">
          <span className="text-[10px] uppercase font-bold tracking-wider text-slate-500">Total Industry average AUM</span>
          <p className="text-xl font-extrabold text-white mt-1 font-mono">{formatCr(summary.total_avg_aum)}</p>
          <p className="text-xs text-slate-400 mt-2">Active tracked AMCs</p>
        </div>

        <div className="glass-card p-6 rounded-xl border border-slate-800/80">
          <span className="text-[10px] uppercase font-bold tracking-wider text-slate-500">Total Industry AAUM Disclosure</span>
          <p className="text-xl font-extrabold text-white mt-1 font-mono">{formatCr(summary.total_aaum)}</p>
          <p className="text-xs text-slate-400 mt-2">Quarterly disclosure metrics</p>
        </div>

        <div className="glass-card p-6 rounded-xl border border-slate-800/80">
          <span className="text-[10px] uppercase font-bold tracking-wider text-slate-500">Total Industry Active Folios</span>
          <p className="text-xl font-extrabold text-indigo-400 mt-1 font-mono">{formatFolios(summary.total_folios)}</p>
          <p className="text-xs text-slate-400 mt-2">Mutual fund unique accounts</p>
        </div>

        <div className="glass-card p-6 rounded-xl border border-slate-800/80 space-y-2">
          <span className="text-[10px] uppercase font-bold tracking-wider text-slate-500 block">Direct vs Regular plan splits</span>
          <div className="flex justify-between items-center text-xs font-semibold">
            <span className="text-emerald-400">Direct: {summary.direct_percentage}%</span>
            <span className="text-slate-400">Regular: {summary.regular_percentage}%</span>
          </div>
          {/* Custom micro-progress bar */}
          <div className="w-full h-2 bg-slate-950 rounded overflow-hidden flex">
            <div className="bg-emerald-500 h-full" style={{ width: `${summary.direct_percentage}%` }} />
            <div className="bg-slate-700 h-full" style={{ width: `${summary.regular_percentage}%` }} />
          </div>
        </div>
      </div>

      {/* Structured Graph Splits */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Category AUM Allocation Breakdowns */}
        <section className="glass-card p-6 rounded-2xl border border-slate-800/80 space-y-4">
          <h4 className="text-sm font-bold text-white uppercase tracking-wider">AUM by Category Classification</h4>
          {categories.length === 0 ? (
            <div className="h-64 flex items-center justify-center text-slate-500 text-xs">
              No category allocations present.
            </div>
          ) : (
            <div className="w-full h-72 flex flex-col sm:flex-row items-center justify-center gap-4">
              <div className="w-full sm:w-1/2 h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={categories}
                      cx="50%"
                      cy="50%"
                      innerRadius={55}
                      outerRadius={75}
                      paddingAngle={3}
                      dataKey="aum_value"
                      nameKey="category"
                    >
                      {categories.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} stroke="rgba(3, 7, 18, 0.5)" strokeWidth={2} />
                      ))}
                    </Pie>
                    <Tooltip
                      content={({ active, payload }) => {
                        if (active && payload && payload.length) {
                          const pt = payload[0];
                          return (
                            <div className="bg-slate-950/90 border border-slate-800 px-3 py-1.5 rounded-lg shadow-xl backdrop-blur-md text-xs font-mono">
                              <span className="text-slate-400 block truncate max-w-[200px]">{pt.name}</span>
                              <span className="font-semibold text-indigo-400 block mt-1">{formatCr(pt.value as number)}</span>
                            </div>
                          );
                        }
                        return null;
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              {/* Legends Grid */}
              <div className="w-full sm:w-1/2 space-y-2 overflow-y-auto max-h-60 pr-2 scrollbar-thin">
                {categories.map((c, idx) => (
                  <div key={c.category} className="flex items-center justify-between text-xs">
                    <div className="flex items-center gap-2 max-w-[70%]">
                      <span className="w-2.5 h-2.5 rounded-full shrink-0" style={{ backgroundColor: COLORS[idx % COLORS.length] }} />
                      <span className="text-slate-300 truncate" title={c.category}>{c.category.replace("Equity Scheme - ", "").replace("Debt Scheme - ", "")}</span>
                    </div>
                    <span className="font-mono font-bold text-slate-200 shrink-0">{c.percentage_of_total?.toFixed(1) || 0}%</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </section>

        {/* AMC League comparisons bar charts */}
        <section className="glass-card p-6 rounded-2xl border border-slate-800/80 space-y-4">
          <h4 className="text-sm font-bold text-white uppercase tracking-wider">AMC Asset League Leaderboard</h4>
          <div className="w-full h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={summary.amcs.slice(0, 5)}
                margin={{ top: 20, right: 10, left: -20, bottom: 0 }}
              >
                <XAxis 
                  dataKey="amc_name" 
                  tickFormatter={(val) => val.split(" ")[0]} 
                  stroke="#475569" 
                  fontSize={10} 
                  fontWeight="semibold"
                />
                <YAxis 
                  stroke="#475569" 
                  fontSize={9} 
                  fontWeight="bold" 
                  tickFormatter={(val) => `₹${(val / 1000).toFixed(0)}k Cr`} 
                />
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const avg = payload[0];
                      const aaum = payload[1];
                      return (
                        <div className="bg-slate-950/90 border border-slate-800 px-3 py-2 rounded-lg shadow-xl backdrop-blur-md text-xs space-y-1">
                          <span className="font-bold text-slate-200 block">{avg.payload.amc_name}</span>
                          <span className="text-slate-400 block">Avg AUM: <strong className="text-indigo-400 font-mono font-bold">{formatCr(avg.value as number)}</strong></span>
                          <span className="text-slate-400 block">AAUM Disclosure: <strong className="text-emerald-400 font-mono font-bold">{formatCr(aaum.value as number)}</strong></span>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Bar dataKey="average_aum" fill="#6366f1" radius={[4, 4, 0, 0]} name="Average AUM" />
                <Bar dataKey="aaum" fill="#10b981" radius={[4, 4, 0, 0]} name="AAUM Disclosure" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>
      </div>

      {/* Main AUM League Table Grid */}
      <section className="bg-slate-900/10 border border-slate-900 rounded-2xl overflow-hidden backdrop-blur-sm">
        <div className="px-6 py-4 border-b border-slate-900 bg-slate-950/30 flex items-center justify-between">
          <h4 className="text-sm font-bold text-white uppercase tracking-wider">AUM & AAUM League Leaderboard</h4>
          <span className="text-[10px] bg-indigo-950/50 text-indigo-300 border border-indigo-900/50 px-2 py-0.5 rounded font-bold font-mono">Period: {summary.period}</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-900/60 bg-slate-950/45 text-slate-400 text-[10px] font-semibold uppercase tracking-wider">
                <th className="py-4 px-6 text-center w-12">Rank</th>
                <th className="py-4 px-6">Mutual Fund House (AMC)</th>
                <th className="py-4 px-6 text-right">Average AUM</th>
                <th className="py-4 px-6 text-right">AAUM Disclosure</th>
                <th className="py-4 px-6 text-right">Direct Splits</th>
                <th className="py-4 px-6 text-right font-mono">Geographic splits (T15 / B15)</th>
                <th className="py-4 px-6 text-center">Folios</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-900/35">
              {summary.amcs.map((a, index) => {
                const directSplitPct = a.direct_aum && a.regular_aum 
                  ? ((a.direct_aum / (a.direct_aum + a.regular_aum)) * 100).toFixed(0) 
                  : null;
                const regSplitPct = directSplitPct ? (100 - Number(directSplitPct)) : null;

                return (
                  <tr 
                    key={a.fund_house_id} 
                    className="hover:bg-slate-900/20 text-xs text-slate-300 transition-colors"
                  >
                    <td className="py-4 px-6 text-center font-bold font-mono text-slate-400">
                      {index + 1}
                    </td>
                    <td className="py-4 px-6 font-semibold text-slate-200">
                      {a.amc_name}
                    </td>
                    <td className="py-4 px-6 text-right font-mono font-semibold text-slate-200">
                      {formatCr(a.average_aum)}
                    </td>
                    <td className="py-4 px-6 text-right font-mono text-slate-200">
                      {formatCr(a.aaum)}
                    </td>
                    <td className="py-4 px-6 text-right space-y-1">
                      {directSplitPct ? (
                        <div className="inline-block text-right w-full">
                          <span className="text-[10px] text-emerald-400 font-bold block leading-none">D: {directSplitPct}% / R: {regSplitPct}%</span>
                          <div className="w-24 h-1.5 bg-slate-950 rounded overflow-hidden mt-1 inline-flex">
                            <div className="bg-emerald-500 h-full" style={{ width: `${directSplitPct}%` }} />
                            <div className="bg-slate-700 h-full" style={{ width: `${regSplitPct}%` }} />
                          </div>
                        </div>
                      ) : (
                        <span className="text-slate-500 text-[10px]">N/A</span>
                      )}
                    </td>
                    <td className="py-4 px-6 text-right font-mono text-slate-400">
                      {a.t15_aum && a.b15_aum ? (
                        <div>
                          <span>₹{a.t15_aum.toLocaleString()} / ₹{a.b15_aum.toLocaleString()}</span>
                        </div>
                      ) : (
                        <span className="text-slate-500">N/A</span>
                      )}
                    </td>
                    <td className="py-4 px-6 text-center font-mono font-medium text-slate-400">
                      {formatFolios(a.folio_count)}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

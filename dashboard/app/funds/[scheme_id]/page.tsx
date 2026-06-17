"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { getFundDetails, getFundNavHistory, simulateSip, FundDetails, NavHistoryPoint, SipSimulationResponse } from "@/lib/api";
import { formatCurrency, formatPercentage } from "@/lib/utils";
import NavLineChart from "@/components/charts/NavLineChart";
import AllocationPieChart from "@/components/charts/AllocationPieChart";
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";
import { FileText, TableProperties, DownloadCloud } from "lucide-react";

export default function FundDetailsPage() {
  const params = useParams();
  const schemeId = parseInt(params.scheme_id as string);

  const [details, setDetails] = useState<FundDetails | null>(null);
  const [navHistory, setNavHistory] = useState<NavHistoryPoint[]>([]);
  const [loading, setLoading] = useState(true);

  // SIP Simulator inputs
  const [monthlyInvest, setMonthlyInvest] = useState(5000);
  const [sipYears, setSipYears] = useState(3);
  const [sipResult, setSipResult] = useState<SipSimulationResponse | null>(null);
  const [sipLoading, setSipLoading] = useState(false);
  const [downloading, setDownloading] = useState<string | null>(null);

  const handleDownload = async (type: 'excel' | 'pdf') => {
    try {
      setDownloading(type);
      const response = await fetch(`http://127.0.0.1:8000/api/v1/reports/fund/${schemeId}/${type}`);
      if (!response.ok) throw new Error("Download failed");
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Fund_${schemeId}_Report.${type === 'excel' ? 'xlsx' : 'pdf'}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error(`Failed to download ${type}:`, error);
      alert(`Failed to download ${type} report.`);
    } finally {
      setDownloading(null);
    }
  };

  useEffect(() => {
    if (!schemeId) return;

    async function loadData() {
      try {
        setLoading(true);
        const det = await getFundDetails(schemeId);
        setDetails(det);

        const history = await getFundNavHistory(schemeId);
        setNavHistory(history);
      } catch (err) {
        console.error("Failed to load scheme analysis details:", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [schemeId]);

  // Recalculate SIP simulation when sliders change
  useEffect(() => {
    if (!schemeId) return;

    setSipLoading(true);
    simulateSip(schemeId, monthlyInvest, sipYears)
      .then(setSipResult)
      .catch((err) => console.error("SIP Simulation failed:", err))
      .finally(() => setSipLoading(false));
  }, [schemeId, monthlyInvest, sipYears]);

  if (loading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="h-10 bg-slate-900 rounded w-1/3" />
        <div className="h-64 bg-slate-900 rounded-xl" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="h-64 bg-slate-900 rounded-xl" />
          <div className="h-64 bg-slate-900 rounded-xl" />
        </div>
      </div>
    );
  }

  if (!details) {
    return (
      <div className="py-12 text-center space-y-4">
        <p className="text-slate-400 text-sm">Mutual Fund Scheme details could not be found.</p>
        <Link href="/funds" className="text-indigo-400 hover:underline text-xs">
          &larr; Back to Fund Explorer
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Top Breadcrumb and Title Header */}
      <div className="space-y-2">
        <Link href="/funds" className="text-xs text-slate-500 hover:text-indigo-400 flex items-center gap-1 font-semibold transition-colors">
          &larr; Back to Fund Explorer
        </Link>
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h2 className="text-2xl font-extrabold text-white">{details.scheme_name}</h2>
            <div className="flex flex-wrap items-center gap-3 text-xs text-slate-500 font-medium mt-1">
              <span className="px-2.5 py-0.5 rounded-full bg-slate-900 text-indigo-400 border border-slate-800">
                {details.category}
              </span>
              <span>•</span>
              <span className="font-mono">ISIN Growth: {details.isin_growth || "N/A"}</span>
            </div>
          </div>
          <div className="text-right">
            <span className="text-[10px] text-slate-500 block uppercase font-bold tracking-wider">Current NAV</span>
            <span className="text-2xl font-black text-indigo-400 font-mono">
              {formatCurrency(details.latest_nav)}
            </span>
          </div>
        </div>

        {/* Action Bar for Reports */}
        <div className="flex flex-wrap items-center gap-3 pt-2">
          <button 
            onClick={() => handleDownload('pdf')}
            disabled={downloading !== null}
            className="flex items-center gap-2 px-4 py-2 bg-rose-600/20 hover:bg-rose-600/30 border border-rose-500/30 text-rose-400 rounded-lg text-xs font-semibold transition-all shadow-sm"
          >
            {downloading === 'pdf' ? <DownloadCloud className="w-4 h-4 animate-bounce" /> : <FileText className="w-4 h-4" />}
            {downloading === 'pdf' ? 'Generating...' : 'Analyst PDF Report'}
          </button>
          
          <button 
            onClick={() => handleDownload('excel')}
            disabled={downloading !== null}
            className="flex items-center gap-2 px-4 py-2 bg-emerald-600/20 hover:bg-emerald-600/30 border border-emerald-500/30 text-emerald-400 rounded-lg text-xs font-semibold transition-all shadow-sm"
          >
            {downloading === 'excel' ? <DownloadCloud className="w-4 h-4 animate-bounce" /> : <TableProperties className="w-4 h-4" />}
            {downloading === 'excel' ? 'Generating...' : 'Data Spreadsheet'}
          </button>
        </div>
      </div>

      {/* Main Splits: Chart and Portfolio Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* NAV Over time Chart Panel */}
        <div className="lg:col-span-2 bg-slate-900/10 border border-slate-900 p-6 rounded-2xl backdrop-blur-md space-y-4">
          <div className="flex justify-between items-center border-b border-slate-900 pb-3">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">NAV Trading History</h3>
            <span className="text-[10px] text-slate-500 font-mono">1 Year Window</span>
          </div>
          <NavLineChart data={navHistory} />
        </div>

        {/* Portfolio distributions and calculations */}
        <div className="bg-slate-900/10 border border-slate-900 p-6 rounded-2xl backdrop-blur-md space-y-6 flex flex-col justify-between">
          <div className="border-b border-slate-900 pb-3">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">Asset Allocations</h3>
          </div>
          <AllocationPieChart data={details.allocations} />
        </div>
      </div>

      {/* Risk Metrics details grid */}
      <div className="grid grid-cols-2 md:grid-cols-6 gap-6 bg-slate-900/10 border border-slate-900 p-6 rounded-2xl backdrop-blur-md">
        <div className="space-y-1">
          <span className="text-[10px] text-slate-500 uppercase font-semibold">1Y Returns (Calc)</span>
          <p className="text-lg font-bold font-mono text-slate-200">{formatPercentage(details.metrics.cagr_1y)}</p>
        </div>
        <div className="space-y-1">
          <span className="text-[10px] text-slate-500 uppercase font-semibold">3Y Returns (Calc)</span>
          <p className="text-lg font-bold font-mono text-slate-200">{formatPercentage(details.metrics.cagr_3y)}</p>
        </div>
        <div className="space-y-1">
          <span className="text-[10px] text-slate-500 uppercase font-semibold">Volatility</span>
          <p className="text-lg font-bold font-mono text-slate-200">{formatPercentage(details.metrics.volatility)}</p>
        </div>
        <div className="space-y-1">
          <span className="text-[10px] text-slate-500 uppercase font-semibold">Sharpe Ratio</span>
          <p className="text-lg font-bold font-mono text-slate-200">{details.metrics.sharpe_ratio?.toFixed(2) || "N/A"}</p>
        </div>
        <div className="space-y-1">
          <span className="text-[10px] text-slate-500 uppercase font-semibold">Sortino</span>
          <p className="text-lg font-bold font-mono text-slate-200">{details.metrics.sortino_ratio?.toFixed(2) || "N/A"}</p>
        </div>
        <div className="space-y-1">
          <span className="text-[10px] text-slate-500 uppercase font-semibold">Max Drawdown</span>
          <p className="text-lg font-bold font-mono text-rose-400">{formatPercentage(details.metrics.max_drawdown)}</p>
        </div>
      </div>

      {/* Dynamic High-Fidelity Side-by-Side Comparison Scorecard */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* Risk Profile & Info */}
        <div className="bg-slate-900/10 border border-slate-900 p-6 rounded-2xl backdrop-blur-md space-y-4">
          <h4 className="text-xs font-bold text-white uppercase tracking-wider border-b border-slate-900 pb-2">Risk Classification & Index</h4>
          <div className="space-y-3 text-xs">
            <div className="flex justify-between items-center">
              <span className="text-slate-500">Benchmark Index:</span>
              <span className="font-semibold text-slate-300 font-sans text-right max-w-[150px] truncate" title={details.benchmark_name || "N/A"}>{details.benchmark_name || "N/A"}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-500">Scheme Riskometer:</span>
              <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${(() => {
                const r = (details.scheme_riskometer || "").toLowerCase();
                if (r.includes("very high")) return "bg-rose-950/40 text-rose-400 border-rose-900/30";
                if (r.includes("high")) return "bg-orange-950/40 text-orange-400 border-orange-900/30";
                if (r.includes("moderately high")) return "bg-amber-950/40 text-amber-400 border-amber-900/30";
                if (r.includes("moderate")) return "bg-yellow-950/40 text-yellow-400 border-yellow-900/30";
                if (r.includes("low")) return "bg-emerald-950/40 text-emerald-400 border-emerald-900/30";
                return "bg-indigo-950/30 text-indigo-400 border-indigo-900/20";
              })()}`}>
                {details.scheme_riskometer || "N/A"}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-500">Benchmark Riskometer:</span>
              <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${(() => {
                const r = (details.benchmark_riskometer || "").toLowerCase();
                if (r.includes("very high")) return "bg-rose-950/40 text-rose-400 border-rose-900/30";
                if (r.includes("high")) return "bg-orange-950/40 text-orange-400 border-orange-900/30";
                if (r.includes("moderately high")) return "bg-amber-950/40 text-amber-400 border-amber-900/30";
                if (r.includes("moderate")) return "bg-yellow-950/40 text-yellow-400 border-yellow-900/30";
                if (r.includes("low")) return "bg-emerald-950/40 text-emerald-400 border-emerald-900/30";
                return "bg-indigo-950/30 text-indigo-400 border-indigo-900/20";
              })()}`}>
                {details.benchmark_riskometer || "N/A"}
              </span>
            </div>
          </div>
        </div>

        {/* 5-Year CAGR Returns Grid */}
        <div className="bg-slate-900/10 border border-slate-900 p-6 rounded-2xl backdrop-blur-md space-y-4">
          <h4 className="text-xs font-bold text-white uppercase tracking-wider border-b border-slate-900 pb-2">5-Year CAGR Performance</h4>
          <div className="space-y-3 text-xs font-mono">
            <div className="flex justify-between">
              <span className="text-slate-500 font-sans">Regular Plan Return:</span>
              <span className="font-bold text-slate-300">{details.regular_cagr_5y !== null ? `${details.regular_cagr_5y.toFixed(2)}%` : "N/A"}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500 font-sans">Direct Plan Return:</span>
              <span className="font-bold text-indigo-400">{details.direct_cagr_5y !== null ? `${details.direct_cagr_5y.toFixed(2)}%` : "N/A"}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500 font-sans">Benchmark Return:</span>
              <span className="font-bold text-slate-400">{details.benchmark_cagr_5y !== null ? `${details.benchmark_cagr_5y.toFixed(2)}%` : "N/A"}</span>
            </div>
          </div>
        </div>

        {/* Asset Metrics & Information Ratio */}
        <div className="bg-slate-900/10 border border-slate-900 p-6 rounded-2xl backdrop-blur-md space-y-4">
          <h4 className="text-xs font-bold text-white uppercase tracking-wider border-b border-slate-900 pb-2">Fund Metrics & Efficiency</h4>
          <div className="space-y-3 text-xs font-sans">
            <div className="flex justify-between">
              <span className="text-slate-500">Regular Info Ratio (5Y):</span>
              <span className="font-bold font-mono text-slate-300">{details.regular_info_ratio !== null ? details.regular_info_ratio.toFixed(2) : "N/A"}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Direct Info Ratio (5Y):</span>
              <span className="font-bold font-mono text-indigo-400">{details.direct_info_ratio !== null ? details.direct_info_ratio.toFixed(2) : "N/A"}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Total Scheme AUM:</span>
              <span className="font-bold font-mono text-indigo-200">
                {details.daily_aum !== null ? `${formatCurrency(details.daily_aum).replace("₹", "")} Cr.` : "N/A"}
              </span>
            </div>
          </div>
        </div>

      </div>

      {/* SIP Compound Simulator Section */}
      <section className="bg-slate-950/40 p-8 rounded-2xl border border-slate-900 backdrop-blur-md space-y-6">
        <div className="border-b border-slate-900 pb-3">
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <svg className="w-5 h-5 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Interactive SIP Portfolio Simulator
          </h3>
          <p className="text-slate-400 text-xs mt-1">
            Simulate an Indian mutual fund monthly SIP investment using historical NAV timeline milestones.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
          {/* Sliders Input Column */}
          <div className="space-y-6 bg-slate-900/20 p-5 rounded-xl border border-slate-900">
            <div className="space-y-2">
              <div className="flex justify-between text-xs font-semibold text-slate-300">
                <span>Monthly Investment</span>
                <span className="font-mono text-indigo-400 font-bold">{formatCurrency(monthlyInvest)}</span>
              </div>
              <input
                type="range"
                min="500"
                max="50000"
                step="500"
                value={monthlyInvest}
                onChange={(e) => setMonthlyInvest(parseInt(e.target.value))}
                className="w-full h-1 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-indigo-600"
              />
              <div className="flex justify-between text-[10px] text-slate-500 font-medium">
                <span>₹500</span>
                <span>₹50,000</span>
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between text-xs font-semibold text-slate-300">
                <span>Duration Period</span>
                <span className="font-mono text-indigo-400 font-bold">{sipYears} {sipYears === 1 ? "Year" : "Years"}</span>
              </div>
              <input
                type="range"
                min="1"
                max="3"
                step="1"
                value={sipYears}
                onChange={(e) => setSipYears(parseInt(e.target.value))}
                className="w-full h-1 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-indigo-600"
              />
              <div className="flex justify-between text-[10px] text-slate-500 font-medium">
                <span>1 Year</span>
                <span>3 Years</span>
              </div>
            </div>

            {/* Results block details */}
            {sipResult && (
              <div className="border-t border-slate-900 pt-4 space-y-3 text-xs">
                <div className="flex justify-between">
                  <span className="text-slate-500">Total Invested:</span>
                  <span className="font-semibold text-slate-200 font-mono">{formatCurrency(sipResult.total_investment)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Wealth Accumulated:</span>
                  <span className="font-semibold text-indigo-400 font-mono">{formatCurrency(sipResult.final_value)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Net Profit Generated:</span>
                  <span className="font-semibold text-emerald-400 font-mono">+{formatCurrency(sipResult.profit)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Absolute Yield:</span>
                  <span className="font-semibold text-emerald-400 font-mono">{formatPercentage(sipResult.absolute_returns)}</span>
                </div>
              </div>
            )}
          </div>

          {/* SIP Chart Visualization Area */}
          <div className="lg:col-span-2 bg-slate-900/10 border border-slate-900 p-5 rounded-xl">
            {sipLoading ? (
              <div className="h-64 flex items-center justify-center text-slate-500 text-sm animate-pulse">
                Running historical SIP model calculations...
              </div>
            ) : sipResult ? (
              <div className="w-full h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={sipResult.chart} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <defs>
                      <linearGradient id="sipValueGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.2} />
                        <stop offset="95%" stopColor="#10b981" stopOpacity={0.0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" opacity={0.3} />
                    <XAxis 
                      dataKey="date" 
                      tickFormatter={(tick) => {
                        try {
                          const d = new Date(tick);
                          return d.toLocaleDateString("en-IN", { month: "short", year: "2-digit" });
                        } catch {
                          return tick;
                        }
                      }}
                      stroke="#64748b" 
                      fontSize={10}
                      tickLine={false}
                    />
                    <YAxis 
                      stroke="#64748b" 
                      fontSize={10}
                      tickLine={false}
                      axisLine={false}
                      tickFormatter={(tick) => `₹${tick}`}
                    />
                    <Tooltip
                      content={({ active, payload }) => {
                        if (active && payload && payload.length) {
                          const pt = payload[0].payload;
                          return (
                            <div className="bg-slate-950/90 border border-slate-800 px-3 py-2 rounded-lg shadow-xl backdrop-blur-md space-y-0.5 text-xs font-mono">
                              <p className="text-[10px] text-slate-500">{new Date(pt.date).toLocaleDateString("en-IN", { month: "long", year: "numeric" })}</p>
                              <p className="text-slate-300">Invested: <span className="font-semibold text-slate-200">{formatCurrency(pt.invested)}</span></p>
                              <p className="text-indigo-400">Value: <span className="font-semibold text-emerald-400">{formatCurrency(pt.value)}</span></p>
                            </div>
                          );
                        }
                        return null;
                      }}
                    />
                    <Area 
                      type="monotone" 
                      dataKey="value" 
                      stroke="#10b981" 
                      strokeWidth={2} 
                      fillOpacity={1} 
                      fill="url(#sipValueGrad)" 
                    />
                    <Area 
                      type="monotone" 
                      dataKey="invested" 
                      stroke="#4f46e5" 
                      strokeWidth={1.5} 
                      strokeDasharray="4 4"
                      fillOpacity={0} 
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="h-64 flex items-center justify-center text-slate-500 text-sm">
                SIP performance simulation chart.
              </div>
            )}
          </div>
        </div>
      </section>
    </div>
  );
}

"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getFunds, getCategories, getAmcs, FundSummary, AmcResponse } from "@/lib/api";
import { formatCurrency, formatPercentage } from "@/lib/utils";

export default function FundTable() {
  const [funds, setFunds] = useState<FundSummary[]>([]);
  const [total, setTotal] = useState(0);
  const [categories, setCategories] = useState<string[]>([]);
  const [amcs, setAmcs] = useState<AmcResponse[]>([]);
  
  const [selectedCategory, setSelectedCategory] = useState("");
  const [selectedAmc, setSelectedAmc] = useState("");
  const [selectedAssetClass, setSelectedAssetClass] = useState("");
  const [selectedType, setSelectedType] = useState(""); // "" (All), "Open Ended", "Close Ended", "Interval Fund"
  const [searchQuery, setSearchQuery] = useState("");
  
  const [limit] = useState(15);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);

  // Load categories and AMCs
  useEffect(() => {
    Promise.all([getCategories(), getAmcs()])
      .then(([catRes, amcRes]) => {
        setCategories(catRes);
        setAmcs(amcRes);
      })
      .catch((err) => console.error("Failed to load controls metadata:", err));
  }, []);

  // Fetch funds when query/category/amc/type/asset_class/page change
  useEffect(() => {
    setLoading(true);
    const offset = (page - 1) * limit;
    getFunds({
      category: selectedCategory || undefined,
      amc_id: selectedAmc ? Number(selectedAmc) : undefined,
      scheme_type: selectedType || undefined,
      asset_class: selectedAssetClass || undefined,
      q: searchQuery || undefined,
      limit,
      offset,
    })
      .then((res) => {
        setFunds(res.funds);
        setTotal(res.total);
      })
      .catch((err) => console.error("Failed to fetch mutual fund schemes:", err))
      .finally(() => setLoading(false));
  }, [selectedCategory, selectedAmc, selectedType, selectedAssetClass, searchQuery, page, limit]);

  const totalPages = Math.ceil(total / limit);

  // Dynamic CSV download of all current filtered list matching side-by-side schema
  const handleExportCSV = async () => {
    try {
      setExporting(true);
      const res = await getFunds({
        category: selectedCategory || undefined,
        amc_id: selectedAmc ? Number(selectedAmc) : undefined,
        scheme_type: selectedType || undefined,
        asset_class: selectedAssetClass || undefined,
        q: searchQuery || undefined,
        limit: 2000,
        offset: 0
      });

      if (res.funds.length === 0) {
        alert("No records to export.");
        return;
      }

      // Generate structured side-by-side comparison CSV matching AMFI's structure
      const headers = [
        "Scheme Code",
        "Scheme Name",
        "Asset Class",
        "Category",
        "Scheme Type",
        "Benchmark Name",
        "Scheme Riskometer",
        "Benchmark Riskometer",
        "Latest NAV (Regular)",
        "Latest NAV (Direct)",
        "5-Year Return (Regular %)",
        "5-Year Return (Direct %)",
        "5-Year Return (Benchmark %)",
        "5-Year Info Ratio (Regular)",
        "5-Year Info Ratio (Direct)",
        "Daily AUM (INR Crores)",
        "NAV Date"
      ];
      
      const rows = res.funds.map((f) => [
        f.scheme_id,
        `"${f.scheme_name.replace(/"/g, '""')}"`,
        `"${f.asset_class || "N/A"}"`,
        `"${f.category}"`,
        `"${f.scheme_type}"`,
        `"${(f.benchmark_name || "").replace(/"/g, '""')}"`,
        `"${f.scheme_riskometer || "N/A"}"`,
        `"${f.benchmark_riskometer || "N/A"}"`,
        f.regular_nav !== null ? f.regular_nav : "N/A",
        f.direct_nav !== null ? f.direct_nav : "N/A",
        f.regular_cagr_5y !== null ? f.regular_cagr_5y : "N/A",
        f.direct_cagr_5y !== null ? f.direct_cagr_5y : "N/A",
        f.benchmark_cagr_5y !== null ? f.benchmark_cagr_5y : "N/A",
        f.regular_info_ratio !== null ? f.regular_info_ratio : "N/A",
        f.direct_info_ratio !== null ? f.direct_info_ratio : "N/A",
        f.daily_aum !== null ? f.daily_aum : "N/A",
        f.latest_date || "N/A"
      ]);

      const csvContent = [headers.join(","), ...rows.map((r) => r.join(","))].join("\n");
      const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.setAttribute("href", url);
      link.setAttribute("download", `AMFI_HighFidelity_Export_${new Date().toISOString().slice(0, 10)}.csv`);
      link.style.visibility = "hidden";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err) {
      console.error("Export failed:", err);
      alert("Failed to export dataset.");
    } finally {
      setExporting(false);
    }
  };

  const getRiskColor = (risk: string | null) => {
    if (!risk) return "bg-slate-900/40 text-slate-400 border-slate-800/45";
    const r = risk.toLowerCase();
    if (r.includes("very high")) return "bg-rose-950/40 text-rose-400 border-rose-900/30";
    if (r.includes("high")) return "bg-orange-950/40 text-orange-400 border-orange-900/30";
    if (r.includes("moderately high")) return "bg-amber-950/40 text-amber-400 border-amber-900/30";
    if (r.includes("moderate")) return "bg-yellow-950/40 text-yellow-400 border-yellow-900/30";
    if (r.includes("low")) return "bg-emerald-950/40 text-emerald-400 border-emerald-900/30";
    return "bg-indigo-950/30 text-indigo-400 border-indigo-900/20";
  };

  return (
    <div className="space-y-6">
      {/* Classification Filters Tabs */}
      <div className="flex border-b border-slate-900 overflow-x-auto gap-2 scrollbar-none">
        {[
          { label: "All Schemes", value: "" },
          { label: "Open Ended Schemes", value: "Open Ended" },
          { label: "Close Ended Schemes", value: "Close Ended" },
          { label: "Interval Funds", value: "Interval Fund" }
        ].map((t) => (
          <button
            key={t.label}
            onClick={() => {
              setSelectedType(t.value);
              setPage(1);
            }}
            className={`px-4 py-2.5 text-xs font-semibold border-b-2 whitespace-nowrap transition-all ${
              selectedType === t.value
                ? "border-indigo-500 text-indigo-400 font-bold"
                : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Filtering and Search Controls */}
      <div className="flex flex-col xl:flex-row gap-3 items-center justify-between bg-slate-900/40 p-4 rounded-xl border border-slate-800/80 backdrop-blur-md">
        
        {/* Search Bar Input */}
        <div className="relative w-full xl:w-64 shrink-0">
          <span className="absolute inset-y-0 left-3 flex items-center text-slate-500">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </span>
          <input
            type="text"
            placeholder="Search schemes..."
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              setPage(1);
            }}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-10 pr-4 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-600 transition-colors"
          />
        </div>

        {/* AMC Dropdown */}
        <div className="w-full xl:w-56 shrink-0">
          <select
            value={selectedAmc}
            onChange={(e) => {
              setSelectedAmc(e.target.value);
              setPage(1);
            }}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-indigo-600 transition-colors"
          >
            <option value="">All AMCs</option>
            {amcs.map((a) => (
              <option key={a.fund_house_id} value={a.fund_house_id}>
                {a.name}
              </option>
            ))}
          </select>
        </div>

        {/* Asset Class Dropdown */}
        <div className="w-full xl:w-44 shrink-0">
          <select
            value={selectedAssetClass}
            onChange={(e) => {
              setSelectedAssetClass(e.target.value);
              setPage(1);
            }}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-indigo-600 transition-colors"
          >
            <option value="">All Asset Classes</option>
            <option value="Equity">Equity</option>
            <option value="Debt">Debt</option>
            <option value="Hybrid">Hybrid</option>
            <option value="Solution Oriented">Solution Oriented</option>
            <option value="Other">Other</option>
          </select>
        </div>

        {/* Category Dropdown Selection */}
        <div className="w-full xl:w-56 shrink-0">
          <select
            value={selectedCategory}
            onChange={(e) => {
              setSelectedCategory(e.target.value);
              setPage(1);
            }}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-indigo-600 transition-colors"
          >
            <option value="">All Categories</option>
            {categories.map((cat) => (
              <option key={cat} value={cat}>
                {cat}
              </option>
            ))}
          </select>
        </div>

        {/* CSV Exporter */}
        <button
          onClick={handleExportCSV}
          disabled={exporting || loading || funds.length === 0}
          className="w-full xl:w-auto ml-auto px-4 py-2 rounded-lg bg-indigo-950/40 hover:bg-indigo-600 border border-indigo-900/40 text-xs font-bold text-indigo-400 hover:text-white flex items-center justify-center gap-1.5 disabled:opacity-40 disabled:hover:bg-transparent disabled:hover:text-indigo-400 disabled:cursor-not-allowed transition-all"
        >
          {exporting ? (
            <span className="w-3.5 h-3.5 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin inline-block" />
          ) : (
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
          )}
          Export structured CSV
        </button>
      </div>

      {/* Main Grid Table */}
      <div className="bg-slate-900/20 border border-slate-900 rounded-xl overflow-hidden backdrop-blur-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse min-w-[1200px]">
            <thead>
              <tr className="border-b border-slate-900/60 bg-slate-950/45 text-slate-400 text-[10px] font-bold uppercase tracking-wider text-center">
                <th className="py-3 px-4 text-left font-mono" rowSpan={2}>Code</th>
                <th className="py-3 px-4 text-left min-w-[280px]" rowSpan={2}>Scheme Name & Details</th>
                <th className="py-3 px-4 text-left min-w-[180px]" rowSpan={2}>Benchmark Index</th>
                <th className="py-3 px-4 text-center border-l border-slate-800/80" colSpan={2}>Riskometers</th>
                <th className="py-3 px-4 text-center border-l border-slate-800/80" colSpan={2}>Latest NAV (INR)</th>
                <th className="py-3 px-4 text-center border-l border-slate-800/80" colSpan={3}>5-Year CAGR Return</th>
                <th className="py-3 px-4 text-center border-l border-slate-800/80" colSpan={2}>5-Year Info Ratio</th>
                <th className="py-3 px-4 text-right border-l border-slate-800/80" rowSpan={2}>AUM (Cr.)</th>
                <th className="py-3 px-4 text-center" rowSpan={2}>Actions</th>
              </tr>
              <tr className="border-b border-slate-900/60 bg-slate-950/30 text-slate-400 text-[9px] font-bold uppercase tracking-wider text-center">
                {/* Riskometers */}
                <th className="py-2 px-2 border-l border-slate-800/80">Scheme</th>
                <th className="py-2 px-2">Benchmark</th>
                
                {/* NAV */}
                <th className="py-2 px-2 border-l border-slate-800/80">Regular</th>
                <th className="py-2 px-2">Direct</th>
                
                {/* Returns */}
                <th className="py-2 px-2 border-l border-slate-800/80">Regular</th>
                <th className="py-2 px-2">Direct</th>
                <th className="py-2 px-2">Benchmark</th>
                
                {/* Info Ratios */}
                <th className="py-2 px-2 border-l border-slate-800/80">Regular</th>
                <th className="py-2 px-2">Direct</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                // Skeletons
                Array.from({ length: 8 }).map((_, idx) => (
                  <tr key={idx} className="border-b border-slate-900/30 animate-pulse text-center">
                    <td className="py-4 px-4 text-left">
                      <div className="h-4 bg-slate-800 rounded w-10" />
                    </td>
                    <td className="py-4 px-4 text-left">
                      <div className="h-4 bg-slate-800 rounded w-60 mb-1.5" />
                      <div className="h-3 bg-slate-800 rounded w-20" />
                    </td>
                    <td className="py-4 px-4 text-left">
                      <div className="h-3.5 bg-slate-800 rounded w-32" />
                    </td>
                    <td className="py-2 px-2 border-l border-slate-800/80">
                      <div className="h-4 bg-slate-800 rounded w-14 mx-auto" />
                    </td>
                    <td className="py-2 px-2">
                      <div className="h-4 bg-slate-800 rounded w-14 mx-auto" />
                    </td>
                    <td className="py-2 px-2 border-l border-slate-800/80">
                      <div className="h-4 bg-slate-800 rounded w-12 mx-auto" />
                    </td>
                    <td className="py-2 px-2">
                      <div className="h-4 bg-slate-800 rounded w-12 mx-auto" />
                    </td>
                    <td className="py-2 px-2 border-l border-slate-800/80">
                      <div className="h-4 bg-slate-800 rounded w-10 mx-auto" />
                    </td>
                    <td className="py-2 px-2">
                      <div className="h-4 bg-slate-800 rounded w-10 mx-auto" />
                    </td>
                    <td className="py-2 px-2">
                      <div className="h-4 bg-slate-800 rounded w-10 mx-auto" />
                    </td>
                    <td className="py-2 px-2 border-l border-slate-800/80">
                      <div className="h-4 bg-slate-800 rounded w-8 mx-auto" />
                    </td>
                    <td className="py-2 px-2">
                      <div className="h-4 bg-slate-800 rounded w-8 mx-auto" />
                    </td>
                    <td className="py-4 px-4 text-right border-l border-slate-800/80">
                      <div className="h-4 bg-slate-800 rounded w-16 ml-auto" />
                    </td>
                    <td className="py-4 px-4">
                      <div className="h-8 bg-slate-800 rounded-lg w-16 mx-auto" />
                    </td>
                  </tr>
                ))
              ) : funds.length === 0 ? (
                <tr>
                  <td colSpan={14} className="py-12 px-6 text-center text-slate-500 text-sm">
                    No mutual fund schemes match your search criteria.
                  </td>
                </tr>
              ) : (
                funds.map((fund) => {
                  return (
                    <tr 
                      key={fund.scheme_id} 
                      className="border-b border-slate-900/30 hover:bg-slate-900/30 text-slate-300 transition-colors text-center text-xs font-mono"
                    >
                      <td className="py-4 px-4 text-left font-mono font-bold text-slate-400">
                        {fund.scheme_id}
                      </td>
                      <td className="py-4 px-4 text-left font-sans">
                        <Link 
                          href={`/funds/${fund.scheme_id}`}
                          className="font-semibold text-slate-200 hover:text-indigo-400 block text-xs transition-colors mb-0.5"
                        >
                          {fund.scheme_name}
                        </Link>
                        <div className="flex flex-wrap items-center gap-1.5 mt-1">
                          <span className="text-[9px] text-slate-400 bg-slate-900 px-1.5 py-0.5 rounded border border-slate-800/80 font-bold">{fund.category}</span>
                          <span className="text-[9px] text-slate-500 bg-slate-950 px-1 py-0.5 rounded font-semibold">{fund.scheme_type}</span>
                        </div>
                      </td>
                      <td className="py-4 px-4 text-left text-[10px] text-slate-400 font-sans font-medium max-w-[200px] truncate" title={fund.benchmark_name || "N/A"}>
                        {fund.benchmark_name || "N/A"}
                      </td>
                      
                      {/* Riskometers */}
                      <td className="py-2 px-2 border-l border-slate-900/60 font-sans">
                        <span className={`inline-block text-[9px] font-bold px-1.5 py-0.5 rounded border ${getRiskColor(fund.scheme_riskometer)}`}>
                          {fund.scheme_riskometer || "N/A"}
                        </span>
                      </td>
                      <td className="py-2 px-2 font-sans">
                        <span className={`inline-block text-[9px] font-bold px-1.5 py-0.5 rounded border ${getRiskColor(fund.benchmark_riskometer)}`}>
                          {fund.benchmark_riskometer || "N/A"}
                        </span>
                      </td>
                      
                      {/* Latest NAVs */}
                      <td className="py-2 px-2 border-l border-slate-900/60 font-bold text-slate-300">
                        {fund.regular_nav !== null ? formatCurrency(fund.regular_nav) : "N/A"}
                      </td>
                      <td className="py-2 px-2 font-bold text-indigo-400">
                        {fund.direct_nav !== null ? formatCurrency(fund.direct_nav) : "N/A"}
                      </td>
                      
                      {/* 5-Year Return CAGRs */}
                      <td className="py-2 px-2 border-l border-slate-900/60 font-bold text-emerald-500">
                        {fund.regular_cagr_5y !== null ? `${fund.regular_cagr_5y.toFixed(2)}%` : "N/A"}
                      </td>
                      <td className="py-2 px-2 font-bold text-emerald-400">
                        {fund.direct_cagr_5y !== null ? `${fund.direct_cagr_5y.toFixed(2)}%` : "N/A"}
                      </td>
                      <td className="py-2 px-2 text-slate-400 font-semibold">
                        {fund.benchmark_cagr_5y !== null ? `${fund.benchmark_cagr_5y.toFixed(2)}%` : "N/A"}
                      </td>
                      
                      {/* 5-Year Info Ratio */}
                      <td className="py-2 px-2 border-l border-slate-900/60 font-semibold text-slate-300">
                        {fund.regular_info_ratio !== null ? fund.regular_info_ratio.toFixed(2) : "N/A"}
                      </td>
                      <td className="py-2 px-2 font-bold text-indigo-400">
                        {fund.direct_info_ratio !== null ? fund.direct_info_ratio.toFixed(2) : "N/A"}
                      </td>
                      
                      {/* Daily AUM (Cr.) */}
                      <td className="py-4 px-4 text-right border-l border-slate-900/60 font-bold text-indigo-200">
                        {fund.daily_aum !== null ? `${formatCurrency(fund.daily_aum).replace("₹", "")}` : "N/A"}
                      </td>
                      
                      <td className="py-4 px-4 text-center font-sans">
                        <Link
                          href={`/funds/${fund.scheme_id}`}
                          className="inline-block text-[10px] font-bold bg-indigo-950/40 hover:bg-indigo-600 border border-indigo-900/40 text-indigo-400 hover:text-white px-2.5 py-1.5 rounded-lg transition-all"
                        >
                          Analyze
                        </Link>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Panel */}
        {!loading && totalPages > 1 && (
          <div className="flex items-center justify-between px-6 py-4 border-t border-slate-900/60 bg-slate-950/20 text-xs text-slate-400">
            <div>
              Showing <span className="font-semibold text-slate-200">{(page - 1) * limit + 1}</span> to{" "}
              <span className="font-semibold text-slate-200">{Math.min(page * limit, total)}</span> of{" "}
              <span className="font-semibold text-slate-200">{total}</span> assets
            </div>
            <div className="flex gap-2">
              <button
                disabled={page === 1}
                onClick={() => setPage(page - 1)}
                className="px-3 py-1.5 rounded bg-slate-900 border border-slate-800 text-slate-300 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-800 transition-colors"
              >
                Previous
              </button>
              <button
                disabled={page === totalPages}
                onClick={() => setPage(page + 1)}
                className="px-3 py-1.5 rounded bg-slate-900 border border-slate-800 text-slate-300 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-800 transition-colors"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

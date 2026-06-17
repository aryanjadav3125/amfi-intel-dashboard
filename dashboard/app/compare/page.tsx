"use client";

import { useEffect, useState } from "react";
import { getFunds, compareFunds, FundSummary, CompareMatrixRow } from "@/lib/api";
import { formatCurrency, formatPercentage } from "@/lib/utils";
import CompareChart from "@/components/charts/CompareChart";

export default function CompareEnginePage() {
  const [availableFunds, setAvailableFunds] = useState<FundSummary[]>([]);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [comparison, setComparison] = useState<{
    matrix: CompareMatrixRow[];
    chart: Array<Record<string, any>>;
  } | null>(null);
  const [loading, setLoading] = useState(false);

  // Load available funds to choose from
  useEffect(() => {
    getFunds({ limit: 100 })
      .then((res) => {
        setAvailableFunds(res.funds);
        // Pre-select first two for demonstration
        if (res.funds.length >= 2) {
          setSelectedIds([res.funds[0].scheme_id, res.funds[1].scheme_id]);
        }
      })
      .catch((err) => console.error("Failed to load compare checklist:", err));
  }, []);

  // Trigger comparison when selected list changes
  useEffect(() => {
    if (selectedIds.length === 0) {
      setComparison(null);
      return;
    }

    setLoading(true);
    compareFunds(selectedIds)
      .then(setComparison)
      .catch((err) => console.error("Comparison request failed:", err))
      .finally(() => setLoading(false));
  }, [selectedIds]);

  const toggleSelect = (id: number) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  };

  return (
    <div className="space-y-8">
      {/* Heading Header */}
      <div>
        <h2 className="text-2xl font-extrabold tracking-tight text-white">Multi-Fund Comparison Engine</h2>
        <p className="text-slate-400 text-sm mt-1">
          Perform overlays across multiple Indian mutual funds, tracking compound performance side-by-side relative to ₹10,000 base values.
        </p>
      </div>

      {/* Selectors and Checkboxes list */}
      <div className="bg-slate-900/20 border border-slate-900 p-6 rounded-2xl backdrop-blur-md space-y-4">
        <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Select Mutual Funds to Compare</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
          {availableFunds.map((fund) => {
            const isChecked = selectedIds.includes(fund.scheme_id);
            return (
              <label 
                key={fund.scheme_id}
                className={`flex items-start gap-3 p-3.5 rounded-xl border text-xs cursor-pointer select-none transition-all ${
                  isChecked 
                    ? "bg-indigo-950/20 border-indigo-500/40 text-slate-100" 
                    : "bg-slate-950/40 border-slate-900 text-slate-400 hover:border-slate-800/80"
                }`}
              >
                <input
                  type="checkbox"
                  checked={isChecked}
                  onChange={() => toggleSelect(fund.scheme_id)}
                  className="mt-0.5 w-4 h-4 rounded text-indigo-600 focus:ring-indigo-500 bg-slate-900 border-slate-800"
                />
                <div>
                  <span className="font-semibold block">{fund.scheme_name}</span>
                  <span className="text-[10px] text-slate-500 mt-0.5 block">{fund.category}</span>
                </div>
              </label>
            );
          })}
        </div>
      </div>

      {/* Comparison results */}
      {selectedIds.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Overlaid returns line chart */}
          <div className="lg:col-span-2 bg-slate-900/10 border border-slate-900 p-6 rounded-2xl backdrop-blur-md space-y-4">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider border-b border-slate-900 pb-3">
              ₹10,000 Compound Investment Growth Series
            </h3>
            {loading ? (
              <div className="h-80 flex items-center justify-center text-slate-500 text-sm animate-pulse">
                Plotting comparative time series growth...
              </div>
            ) : comparison ? (
              <CompareChart 
                data={comparison.chart} 
                schemes={comparison.matrix.map((m) => ({ scheme_id: m.scheme_id, scheme_name: m.scheme_name }))} 
              />
            ) : null}
          </div>

          {/* Metrics matrix grid comparisons */}
          <div className="bg-slate-900/10 border border-slate-900 p-6 rounded-2xl backdrop-blur-md space-y-4">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider border-b border-slate-900 pb-3">
              Risk & return comparisons
            </h3>
            <div className="space-y-4 overflow-y-auto max-h-[320px] pr-2">
              {loading ? (
                Array.from({ length: 2 }).map((_, idx) => (
                  <div key={idx} className="h-28 bg-slate-900 rounded-xl animate-pulse" />
                ))
              ) : comparison ? (
                comparison.matrix.map((row) => (
                  <div 
                    key={row.scheme_id} 
                    className="p-4 rounded-xl bg-slate-950/60 border border-slate-900 space-y-2 text-xs"
                  >
                    <h4 className="font-bold text-slate-200 truncate">{row.scheme_name}</h4>
                    <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400">
                      <div>
                        <span className="text-slate-500">1Y Returns:</span>
                        <span className="font-semibold block text-slate-300">{formatPercentage(row.cagr_1y)}</span>
                      </div>
                      <div>
                        <span className="text-slate-500">Volatility:</span>
                        <span className="font-semibold block text-slate-300">{formatPercentage(row.volatility)}</span>
                      </div>
                      <div>
                        <span className="text-slate-500">Sharpe Ratio:</span>
                        <span className="font-semibold block text-indigo-400">{row.sharpe_ratio?.toFixed(2) || "N/A"}</span>
                      </div>
                      <div>
                        <span className="text-slate-500">Max DD:</span>
                        <span className="font-semibold block text-rose-400">{formatPercentage(row.max_drawdown)}</span>
                      </div>
                    </div>
                  </div>
                ))
              ) : null}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

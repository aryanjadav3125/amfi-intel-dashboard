"use client";

import { useState } from "react";
import useSWR from "swr";
import { calculatePortfolioOverlap, PortfolioOverlapResponse, getFunds } from "@/lib/api";
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip as RechartsTooltip, Legend } from "recharts";

const COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#8b5cf6', '#ec4899', '#0ea5e9'];

export default function PortfolioLab() {
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [funds, setFunds] = useState<{ id: number; name: string; allocation: number }[]>([]);
  const [overlapData, setOverlapData] = useState<PortfolioOverlapResponse | null>(null);

  // Search hook
  const { data: searchResults, isLoading: searching } = useSWR(
    searchQuery.length > 2 ? `/funds?q=${searchQuery}&limit=5` : null, 
    () => getFunds({ q: searchQuery, limit: 5 })
  );

  const addFund = (fund: any) => {
    if (funds.find(f => f.id === fund.scheme_id)) return;
    setFunds([...funds, { id: fund.scheme_id, name: fund.scheme_name, allocation: 0 }]);
    setSearchQuery("");
  };

  const removeFund = (id: number) => {
    setFunds(funds.filter(f => f.id !== id));
  };

  const simulateHoldings = async () => {
    if (funds.length < 2) {
      alert("Please add at least 2 funds to simulate portfolio.");
      return;
    }
    try {
      setLoading(true);
      const res = await calculatePortfolioOverlap(funds.map(f => f.id));
      setOverlapData(res);
    } catch (error) {
      console.error(error);
      alert("Failed to calculate overlap. Ensure funds exist in database.");
    } finally {
      setLoading(false);
    }
  };

  const sectorData = overlapData 
    ? Object.entries(overlapData.sector_similarity).map(([name, value]) => ({ name, value }))
    : [];

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-3xl font-extrabold tracking-tight text-white font-heading">Portfolio Lab</h2>
          <p className="text-slate-400 text-sm mt-1 max-w-2xl">
            Simulate combinations of mutual funds to detect holdings overlap, sector concentration, and overall risk diversification before investing.
          </p>
        </div>
        <button 
          onClick={simulateHoldings}
          disabled={loading}
          className="bg-primary hover:bg-emerald-500 disabled:opacity-50 text-white text-sm font-semibold px-4 py-2.5 rounded-lg shadow-lg shadow-emerald-600/20 hover:shadow-emerald-600/40 transition-all"
        >
          {loading ? "Simulating..." : "Simulate Holdings"}
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Col: Fund Selector */}
        <section className="bg-surface border border-border p-6 rounded-2xl flex flex-col gap-4">
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            Selected Funds
          </h3>
          
          {/* Search Input */}
          <div className="relative">
            <input 
              type="text"
              placeholder="Search and add fund..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-background border border-border text-sm text-slate-200 px-4 py-2 rounded focus:outline-none focus:border-primary"
            />
            {searchQuery.length > 2 && (
              <div className="absolute z-10 w-full mt-1 bg-surfaceHighlight border border-border rounded shadow-2xl max-h-64 overflow-y-auto">
                {searching ? (
                  <div className="p-3 text-xs text-neutral">Searching...</div>
                ) : searchResults?.funds.length === 0 ? (
                  <div className="p-3 text-xs text-neutral">No funds found.</div>
                ) : (
                  searchResults?.funds.map((f: any) => (
                    <button 
                      key={f.scheme_id} 
                      onClick={() => addFund(f)}
                      className="w-full text-left p-3 hover:bg-surface border-b border-border text-sm text-slate-300 transition-colors"
                    >
                      <div className="font-semibold truncate">{f.scheme_name}</div>
                      <div className="text-[10px] text-neutral">{f.category}</div>
                    </button>
                  ))
                )}
              </div>
            )}
          </div>

          <div className="space-y-3 mt-2">
             {funds.map((f, i) => (
                <div key={i} className="p-4 bg-surfaceHighlight border border-border rounded-xl relative group">
                    <button 
                      onClick={() => removeFund(f.id)}
                      className="absolute top-2 right-2 text-neutral hover:text-negative opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      &times;
                    </button>
                    <div className="font-semibold text-white text-sm pr-4">{f.name}</div>
                    <div className="text-xs text-neutral mt-2 flex items-center gap-2">
                      Allocation: 
                      <input 
                        type="number" 
                        value={f.allocation}
                        onChange={(e) => {
                          const newFunds = [...funds];
                          newFunds[i].allocation = Number(e.target.value);
                          setFunds(newFunds);
                        }}
                        className="bg-transparent border-b border-neutral/50 w-12 text-white outline-none focus:border-primary"
                      />%
                    </div>
                </div>
             ))}
          </div>
        </section>

        {/* Right Col: Overlap Visualizer */}
        <section className="lg:col-span-2 space-y-6">
          <div className="bg-surface border border-border p-6 rounded-2xl">
             <h3 className="text-lg font-bold text-white flex items-center gap-2 mb-4">
               Portfolio Overlap Intelligence
             </h3>
             
             {!overlapData && !loading ? (
               <div className="h-64 flex items-center justify-center border border-dashed border-border rounded-xl bg-surfaceHighlight/50 text-neutral text-sm">
                 Add funds and click 'Simulate Holdings' to view analysis.
               </div>
             ) : loading ? (
               <div className="h-64 flex items-center justify-center border border-dashed border-border rounded-xl bg-surfaceHighlight/50 text-neutral text-sm animate-pulse">
                 Calculating Overlap Matrix...
               </div>
             ) : (
               <>
                 <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
                    <div className="p-5 bg-surfaceHighlight rounded-xl border border-border shadow-sm">
                        <div className="text-[10px] text-neutral uppercase font-bold tracking-wider">Overlap Risk</div>
                        <div className="text-2xl font-bold text-white mt-1">{overlapData?.overlap_percentage}%</div>
                        <div className="w-full bg-background h-1.5 rounded-full mt-3">
                            <div className="bg-negative h-1.5 rounded-full shadow-lg shadow-negative/50" style={{width: `${Math.min(overlapData?.overlap_percentage || 0, 100)}%`}}></div>
                        </div>
                    </div>
                    <div className="p-5 bg-surfaceHighlight rounded-xl border border-border shadow-sm">
                        <div className="text-[10px] text-neutral uppercase font-bold tracking-wider">Diversification Score</div>
                        <div className="text-2xl font-bold text-primary mt-1">{overlapData?.diversification_score}/100</div>
                        <div className="w-full bg-background h-1.5 rounded-full mt-3">
                            <div className="bg-primary h-1.5 rounded-full shadow-lg shadow-primary/50" style={{width: `${overlapData?.diversification_score || 0}%`}}></div>
                        </div>
                    </div>
                    <div className="p-5 bg-surfaceHighlight rounded-xl border border-border shadow-sm flex flex-col justify-center col-span-2 md:col-span-1">
                        <div className="text-[10px] text-neutral uppercase font-bold tracking-wider mb-2">Common Holdings</div>
                        <div className="flex flex-wrap gap-2">
                            {overlapData?.common_holdings.map((c, i) => (
                                <span key={i} className="text-[10px] px-2 py-1 bg-background text-slate-300 rounded border border-border truncate max-w-[120px]">{c}</span>
                            ))}
                            {overlapData?.common_holdings?.length === 0 && <span className="text-xs text-neutral">No overlap detected.</span>}
                        </div>
                    </div>
                 </div>
                 
                 {/* Sector Visualization */}
                 <div className="mt-6 h-72 border border-border rounded-xl flex flex-col items-center justify-center bg-surfaceHighlight/30 pt-4">
                    <h4 className="text-xs text-neutral uppercase font-bold tracking-wider mb-2">Sector Exposure</h4>
                    {sectorData.length > 0 ? (
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={sectorData}
                            cx="50%"
                            cy="50%"
                            innerRadius={60}
                            outerRadius={90}
                            paddingAngle={5}
                            dataKey="value"
                            stroke="none"
                          >
                            {sectorData.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                          </Pie>
                          <RechartsTooltip 
                            contentStyle={{ backgroundColor: '#111827', borderColor: '#1e293b', borderRadius: '8px', fontSize: '12px' }}
                            itemStyle={{ color: '#fff' }}
                            formatter={(value: number) => [`${value}%`, 'Allocation']}
                          />
                          <Legend verticalAlign="bottom" height={36} iconType="circle" wrapperStyle={{ fontSize: '11px', color: '#64748b' }}/>
                        </PieChart>
                      </ResponsiveContainer>
                    ) : (
                      <p className="text-neutral text-sm flex-1 flex items-center justify-center">Not enough data to map sectors.</p>
                    )}
                 </div>
               </>
             )}
          </div>
        </section>

      </div>
    </div>
  );
}

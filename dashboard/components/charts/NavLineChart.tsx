"use client";

import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";
import { formatCurrency, formatDate } from "@/lib/utils";

interface NavHistoryPoint {
  date: string;
  nav: number;
  regular_nav?: number | null;
}

interface NavLineChartProps {
  data: NavHistoryPoint[];
}

export default function NavLineChart({ data }: NavLineChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-slate-500 text-sm">
        No historical NAV data points available for the chosen window.
      </div>
    );
  }

  // Parse and format dates for chart labels
  const chartData = data.map((d) => ({
    ...d,
    formattedDate: formatDate(d.date),
  }));

  // Find min/max for scale optimization
  const navValues = data.map((d) => d.nav);
  const regularValues = data.map((d) => d.regular_nav).filter((v): v is number => typeof v === "number" && !isNaN(v));
  const allValues = [...navValues, ...regularValues];
  
  const minNav = Math.min(...allValues);
  const maxNav = Math.max(...allValues);
  const yDomain = [Math.floor(minNav * 0.98), Math.ceil(maxNav * 1.02)];

  return (
    <div className="w-full h-72">
      <div className="flex items-center gap-4 justify-end text-[10px] font-bold tracking-wider uppercase mb-2">
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-0.5 bg-indigo-500 inline-block" />
          <span className="text-indigo-400">Direct Plan</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-0.5 bg-purple-500 border-dashed inline-block" />
          <span className="text-purple-400">Regular Plan</span>
        </div>
      </div>
      
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <defs>
            <linearGradient id="directGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#4f46e5" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#4f46e5" stopOpacity={0.0} />
            </linearGradient>
            <linearGradient id="regularGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#a855f7" stopOpacity={0.15} />
              <stop offset="95%" stopColor="#a855f7" stopOpacity={0.0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" opacity={0.3} />
          <XAxis 
            dataKey="date" 
            tickFormatter={(tick) => {
              try {
                const parts = tick.split("-");
                if (parts.length === 3) {
                  const d = new Date(tick);
                  return d.toLocaleDateString("en-IN", { month: "short", year: "2-digit" });
                }
                return tick;
              } catch {
                return tick;
              }
            }}
            stroke="#64748b" 
            fontSize={10}
            tickLine={false}
          />
          <YAxis 
            domain={yDomain} 
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
                  <div className="bg-slate-950/95 border border-slate-800 px-3 py-2 rounded-lg shadow-xl backdrop-blur-md space-y-1">
                    <p className="text-[10px] text-slate-500 font-mono">{pt.formattedDate}</p>
                    <p className="text-xs font-semibold font-mono">
                      Direct NAV: <span className="text-indigo-400 font-bold">{formatCurrency(pt.nav)}</span>
                    </p>
                    {pt.regular_nav !== undefined && pt.regular_nav !== null && (
                      <p className="text-xs font-semibold font-mono">
                        Regular NAV: <span className="text-purple-400 font-bold">{formatCurrency(pt.regular_nav)}</span>
                      </p>
                    )}
                  </div>
                );
              }
              return null;
            }}
          />
          <Area 
            type="monotone" 
            dataKey="nav" 
            stroke="#6366f1" 
            strokeWidth={2} 
            fillOpacity={1} 
            fill="url(#directGradient)" 
          />
          <Area 
            type="monotone" 
            dataKey="regular_nav" 
            stroke="#a855f7" 
            strokeWidth={1.5} 
            strokeDasharray="4 4"
            fillOpacity={1} 
            fill="url(#regularGradient)" 
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

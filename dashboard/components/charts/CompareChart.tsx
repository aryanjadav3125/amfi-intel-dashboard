"use client";

import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, Legend } from "recharts";
import { formatCurrency, formatDate } from "@/lib/utils";

interface CompareChartProps {
  data: Array<Record<string, any>>;
  schemes: Array<{ scheme_id: number; scheme_name: string }>;
}

const LINE_COLORS = ["#6366f1", "#10b981", "#f59e0b", "#ec4899", "#8b5cf6", "#3b82f6"];

export default function CompareChart({ data, schemes }: CompareChartProps) {
  if (!data || data.length === 0 || !schemes || schemes.length === 0) {
    return (
      <div className="h-72 flex items-center justify-center text-slate-500 text-sm">
        Add mutual funds above to overlay their historical compound returns.
      </div>
    );
  }

  // Parse and sort unique keys representing scheme IDs (keys like "scheme_120847")
  const schemeKeys = schemes.map((s) => `scheme_${s.scheme_id}`);

  // Format dates inside chart data
  const chartData = data.map((d) => ({
    ...d,
    formattedDate: formatDate(d.date),
  }));

  return (
    <div className="w-full h-80">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData} margin={{ top: 15, right: 10, left: -10, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" opacity={0.2} />
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
                  <div className="bg-slate-950/90 border border-slate-800 p-3 rounded-lg shadow-xl backdrop-blur-md space-y-1.5 min-w-[200px]">
                    <p className="text-[10px] text-slate-500 font-mono border-b border-slate-900 pb-1">{pt.formattedDate}</p>
                    <div className="space-y-1">
                      {payload.map((item) => {
                        const nameStr = item.name !== undefined && item.name !== null ? String(item.name) : "";
                        const schemeId = parseInt(nameStr.replace("scheme_", "") || "0");
                        const schemeObj = schemes.find((s) => s.scheme_id === schemeId);
                        return (
                          <div key={item.name} className="flex justify-between items-center text-xs gap-4">
                            <span 
                              className="font-medium truncate max-w-[140px] text-slate-300"
                              style={{ color: item.stroke }}
                            >
                              {schemeObj?.scheme_name || nameStr}
                            </span>
                            <span className="font-semibold text-white font-mono">
                              {formatCurrency(item.value as number)}
                            </span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                );
              }
              return null;
            }}
          />
          <Legend 
            verticalAlign="top" 
            height={36}
            iconType="circle"
            iconSize={8}
            formatter={(value) => {
              const valStr = value !== undefined && value !== null ? String(value) : "";
              const schemeId = parseInt(valStr.replace("scheme_", ""));
              const schemeObj = schemes.find((s) => s.scheme_id === schemeId);
              return (
                <span className="text-xs text-slate-300 font-medium hover:text-white transition-colors">
                  {schemeObj?.scheme_name || valStr}
                </span>
              );
            }}
          />
          {schemeKeys.map((key, index) => (
            <Line
              key={key}
              type="monotone"
              dataKey={key}
              name={key}
              stroke={LINE_COLORS[index % LINE_COLORS.length]}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, strokeWidth: 0 }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

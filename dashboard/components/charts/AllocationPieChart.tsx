"use client";

import { ResponsiveContainer, PieChart, Pie, Cell, Legend, Tooltip } from "recharts";

interface AssetAllocation {
  asset_class: string;
  percentage: number;
}

interface AllocationPieChartProps {
  data: AssetAllocation[];
}

const COLORS = ["#6366f1", "#10b981", "#f59e0b", "#ec4899", "#8b5cf6"];

export default function AllocationPieChart({ data }: AllocationPieChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-slate-500 text-sm">
        No asset class allocation breakdowns are available.
      </div>
    );
  }

  // Filter out any zero values to avoid clutter
  const filteredData = data.filter((d) => d.percentage > 0);

  return (
    <div className="w-full h-64 flex items-center justify-center">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={filteredData}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={80}
            paddingAngle={4}
            dataKey="percentage"
            nameKey="asset_class"
          >
            {filteredData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} stroke="rgba(3, 7, 18, 0.5)" strokeWidth={2} />
            ))}
          </Pie>
          <Tooltip
            content={({ active, payload }) => {
              if (active && payload && payload.length) {
                const pt = payload[0];
                return (
                  <div className="bg-slate-950/90 border border-slate-800 px-3 py-1.5 rounded-lg shadow-xl backdrop-blur-md text-xs font-mono">
                    <span className="text-slate-400">{pt.name}: </span>
                    <span className="font-semibold text-indigo-400">{(pt.value as number).toFixed(2)}%</span>
                  </div>
                );
              }
              return null;
            }}
          />
          <Legend 
            verticalAlign="bottom" 
            height={36} 
            iconType="circle"
            iconSize={8}
            formatter={(value) => <span className="text-xs text-slate-300 font-medium">{value}</span>}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}

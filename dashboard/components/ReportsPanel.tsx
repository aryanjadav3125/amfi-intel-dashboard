"use client";

import { useEffect, useState } from "react";
import { getAmcs, AmcResponse } from "@/lib/api";

export default function ReportsPanel() {
  const [amcs, setAmcs] = useState<AmcResponse[]>([]);
  const [selectedAmc, setSelectedAmc] = useState("");
  const [selectedType, setSelectedType] = useState("");
  const [fromDate, setFromDate] = useState("");
  const [toDate, setToDate] = useState("");
  
  const [loadingAmcs, setLoadingAmcs] = useState(true);
  const [errorMsg, setErrorMsg] = useState("");

  useEffect(() => {
    getAmcs()
      .then(setAmcs)
      .catch((err) => console.error("Failed to load AMCs:", err))
      .finally(() => setLoadingAmcs(false));
  }, []);

  const handleDownloadRaw = (type: string) => {
    window.open(`http://127.0.0.1:8000/api/v1/reports/download?type=${type}`, "_blank");
  };

  const handleHistorySubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg("");

    if (!fromDate || !toDate) {
      setErrorMsg("Please select both From Date and To Date.");
      return;
    }

    const start = new Date(fromDate);
    const end = new Date(toDate);
    const diffTime = Math.abs(end.getTime() - start.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (start > end) {
      setErrorMsg("From Date cannot be later than To Date.");
      return;
    }

    if (diffDays > 90) {
      setErrorMsg("AMFI India restricts historical downloads to a maximum of 90 days at a time.");
      return;
    }

    // Build URL
    const params = new URLSearchParams();
    if (selectedAmc) params.append("mf", selectedAmc);
    if (selectedType) params.append("tp", selectedType);
    params.append("from_date", fromDate);
    params.append("to_date", toDate);

    window.open(`http://127.0.0.1:8000/api/v1/reports/history?${params.toString()}`, "_blank");
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Download raw report files */}
      <section className="space-y-4">
        <div>
          <h3 className="text-lg font-bold text-white">Download Daily NAV Reports</h3>
          <p className="text-slate-400 text-xs mt-0.5">
            Download plain-text reports directly from AMFI India for all classifications.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6">
          {[
            { key: "all", title: "Complete NAV Report", desc: "Includes all active schemes (NAVAll.txt)" },
            { key: "open", title: "Open Ended NAV Report", desc: "Equity, hybrid & debt schemes (NAVOpen.txt)" },
            { key: "close", title: "Close Ended NAV Report", desc: "Closed schemes and ETFs (NAVClose.txt)" },
            { key: "interval", title: "Interval Fund NAV Report", desc: "Special interval term schemes (NAVInterval.txt)" }
          ].map((item) => (
            <div 
              key={item.key}
              className="glass-card p-5 rounded-xl border border-slate-800/80 flex flex-col justify-between hover:border-indigo-500/45 transition-all group"
            >
              <div className="space-y-2">
                <span className="w-8 h-8 rounded-lg bg-indigo-950/50 border border-indigo-900/30 flex items-center justify-center text-indigo-400 text-xs font-bold">
                  TXT
                </span>
                <h4 className="font-semibold text-slate-200 text-sm">{item.title}</h4>
                <p className="text-[11px] text-slate-500">{item.desc}</p>
              </div>
              
              <button
                onClick={() => handleDownloadRaw(item.key)}
                className="mt-5 w-full bg-slate-950 hover:bg-indigo-600 border border-slate-800 group-hover:border-indigo-500 text-xs font-semibold text-slate-300 group-hover:text-white py-2 rounded-lg flex items-center justify-center gap-1.5 transition-all"
              >
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                Download Report
              </button>
            </div>
          ))}
        </div>
      </section>

      {/* Historical downloads */}
      <section className="bg-slate-900/10 border border-slate-900 p-6 rounded-2xl backdrop-blur-md space-y-6">
        <div>
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <svg className="w-5 h-5 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Historical NAV Query Engine
          </h3>
          <p className="text-slate-400 text-xs mt-1">
            Specify a target Asset Management Company, scheme class, and dates. Queries the portal dynamically.
          </p>
        </div>

        <form onSubmit={handleHistorySubmit} className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {/* AMC Dropdown */}
          <div className="space-y-1.5">
            <label className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">Mutual Fund House</label>
            <select
              value={selectedAmc}
              onChange={(e) => setSelectedAmc(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2.5 text-xs text-slate-100 focus:outline-none focus:border-indigo-600 transition-colors"
            >
              <option value="">Select Mutual Fund (All)</option>
              {amcs.map((a) => (
                <option key={a.fund_house_id} value={a.fund_house_id}>
                  {a.name}
                </option>
              ))}
            </select>
          </div>

          {/* Scheme Type */}
          <div className="space-y-1.5">
            <label className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">Scheme Class Type</label>
            <select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2.5 text-xs text-slate-100 focus:outline-none focus:border-indigo-600 transition-colors"
            >
              <option value="">Select Type (All)</option>
              <option value="Open">Open Ended</option>
              <option value="Close">Close Ended</option>
              <option value="Interval">Interval Fund</option>
            </select>
          </div>

          {/* From Date */}
          <div className="space-y-1.5">
            <label className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">From Date</label>
            <input
              type="date"
              value={fromDate}
              onChange={(e) => setFromDate(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2.5 text-xs text-slate-100 focus:outline-none focus:border-indigo-600 transition-colors font-mono"
            />
          </div>

          {/* To Date */}
          <div className="space-y-1.5">
            <label className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">To Date</label>
            <input
              type="date"
              value={toDate}
              onChange={(e) => setToDate(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2.5 text-xs text-slate-100 focus:outline-none focus:border-indigo-600 transition-colors font-mono"
            />
          </div>

          {errorMsg && (
            <div className="md:col-span-4 bg-rose-950/40 border border-rose-900/30 text-rose-400 text-xs px-4 py-3 rounded-lg flex items-center gap-2">
              <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              {errorMsg}
            </div>
          )}

          <div className="md:col-span-4 flex items-center justify-between border-t border-slate-900/60 pt-4 text-xs text-slate-500">
            <div className="flex items-center gap-1.5 text-amber-500 font-medium">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Maximum query range is restricted to 90 days.
            </div>
            <button
              type="submit"
              className="bg-indigo-600 hover:bg-indigo-500 text-white font-semibold px-6 py-2.5 rounded-lg shadow-lg shadow-indigo-600/10 hover:shadow-indigo-600/25 transition-all text-xs flex items-center gap-1.5"
            >
              Get Report
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
              </svg>
            </button>
          </div>
        </form>
      </section>
    </div>
  );
}

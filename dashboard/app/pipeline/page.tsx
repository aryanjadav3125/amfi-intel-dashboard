"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getPipelineStatus, PipelineStatus } from "@/lib/api";
import { formatDate } from "@/lib/utils";

export default function PipelineAuditsPage() {
  const [pipeline, setPipeline] = useState<PipelineStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchStatus() {
      try {
        setLoading(true);
        const status = await getPipelineStatus();
        setPipeline(status);
      } catch (err) {
        console.error("Failed to load pipeline audits:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchStatus();
  }, []);

  return (
    <div className="space-y-8">
      {/* Page header title */}
      <div>
        <h2 className="text-2xl font-extrabold tracking-tight text-white">Scraper & Data Pipeline Auditing</h2>
        <p className="text-slate-400 text-sm mt-1">
          Monitor daily ingestion jobs, audit data parsing consistency, and view scheduler job status logs.
        </p>
      </div>

      {/* Main details list */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* Execution audit log card */}
        <div className="md:col-span-2 bg-slate-900/10 border border-slate-900 p-6 rounded-2xl backdrop-blur-md space-y-6">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider border-b border-slate-900 pb-3">
            Latest Execution Audit Trail
          </h3>

          {loading ? (
            <div className="space-y-4 animate-pulse">
              <div className="h-10 bg-slate-800 rounded w-full" />
              <div className="h-10 bg-slate-800 rounded w-full" />
            </div>
          ) : !pipeline || pipeline.run_id === null ? (
            <div className="py-8 text-center text-slate-500 text-sm">
              No daily scraper executions logged in the database yet.
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 text-sm">
              <div className="space-y-1">
                <span className="text-[10px] text-slate-500 uppercase block font-bold">Execution ID</span>
                <span className="font-mono text-slate-200 font-semibold">Run #{pipeline.run_id}</span>
              </div>

              <div className="space-y-1">
                <span className="text-[10px] text-slate-500 uppercase block font-bold">Execution Class</span>
                <span className="font-semibold capitalize text-slate-200">{pipeline.run_type} Ingestion</span>
              </div>

              <div className="space-y-1">
                <span className="text-[10px] text-slate-500 uppercase block font-bold">Start Boundary</span>
                <span className="font-semibold text-slate-200">{formatDate(pipeline.started_at)}</span>
              </div>

              <div className="space-y-1">
                <span className="text-[10px] text-slate-500 uppercase block font-bold">Completed Boundary</span>
                <span className="font-semibold text-slate-200">{formatDate(pipeline.completed_at)}</span>
              </div>

              <div className="space-y-1">
                <span className="text-[10px] text-slate-500 uppercase block font-bold">Records Upserted</span>
                <span className="font-semibold text-emerald-400 font-mono">+{pipeline.records_inserted} rows</span>
              </div>

              <div className="space-y-1">
                <span className="text-[10px] text-slate-500 uppercase block font-bold">Omitted Rows</span>
                <span className="font-semibold text-slate-400 font-mono">{pipeline.records_skipped} rows</span>
              </div>

              <div className="space-y-1">
                <span className="text-[10px] text-slate-500 uppercase block font-bold">Omitted Errors</span>
                <span className={`font-semibold font-mono ${
                  pipeline.errors_count > 0 ? "text-rose-400" : "text-slate-400"
                }`}>{pipeline.errors_count} rows</span>
              </div>

              <div className="space-y-1">
                <span className="text-[10px] text-slate-500 uppercase block font-bold">Execution Status</span>
                <span className={`inline-block text-xs font-bold px-2 py-0.5 rounded capitalize ${
                  pipeline.status === "success" 
                    ? "bg-emerald-950/40 text-emerald-400 border border-emerald-900/30" 
                    : "bg-amber-950/40 text-amber-400 border border-amber-900/30"
                }`}>
                  {pipeline.status}
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Click Command CLI panel */}
        <div className="bg-slate-900/10 border border-slate-900 p-6 rounded-2xl backdrop-blur-md space-y-6">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider border-b border-slate-900 pb-3">
            Scheduler CLI Backfills
          </h3>
          
          <div className="space-y-4 text-xs">
            <p className="text-slate-400 leading-relaxed">
              Use the built-in click CLI hooks inside the virtual environment terminal to manually backfill historical date ranges.
            </p>

            <div className="space-y-2.5">
              <span className="text-[10px] text-slate-500 uppercase font-bold block">Run Daily Sync</span>
              <pre className="bg-slate-950 border border-slate-800 p-3 rounded-lg font-mono text-indigo-300 overflow-x-auto text-[10px]">
                python -m scheduler.cli run-now
              </pre>
            </div>

            <div className="space-y-2.5">
              <span className="text-[10px] text-slate-500 uppercase font-bold block">Bulk Historical backfill</span>
              <pre className="bg-slate-950 border border-slate-800 p-3 rounded-lg font-mono text-indigo-300 overflow-x-auto text-[10px]">
                python -m scheduler.cli backfill --from 2023-01-01 --to 2023-12-31
              </pre>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

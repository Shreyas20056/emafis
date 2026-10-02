"use client";

import { Cpu, ShieldCheck, Database, GitBranch } from "lucide-react";

export default function Footer() {
  return (
    <footer className="mt-auto border-t border-slate-800/80 bg-[#070a0f] py-8 text-slate-400">
      <div className="mx-auto max-w-[1800px] px-4 lg:px-7">
        <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800/60 pb-6">
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg border border-cyan-500/30 bg-cyan-500/10 text-cyan-400">
              <Cpu className="h-4 w-4" />
            </div>
            <div>
              <span className="font-mono text-sm font-bold text-slate-200">
                EMAFIS Research Platform
              </span>
              <p className="text-[11px] text-slate-400">
                Explainable Multi-Agent Financial Intelligence System
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4 font-mono text-[11px] text-slate-400">
            <span className="flex items-center gap-1">
              <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
              API Status: Online
            </span>
            <span className="flex items-center gap-1">
              <Database className="h-3.5 w-3.5 text-cyan-400" />
              MongoDB Connected
            </span>
            <span className="flex items-center gap-1">
              <ShieldCheck className="h-3.5 w-3.5 text-cyan-400" />
              XAI Engine Active
            </span>
          </div>
        </div>

        <div className="mt-6 flex flex-wrap items-center justify-between gap-4 text-xs text-slate-400 font-mono">
          <p>© 2026 EMAFIS Research Team. All rights reserved.</p>
          <div className="flex items-center gap-4 text-[11px]">
            <span>Adaptive Dynamic Weighting</span>
            <span>•</span>
            <span>Multi-Agent Architecture</span>
            <span>•</span>
            <span>Llama 3.3 XAI</span>
          </div>
        </div>
      </div>
    </footer>
  );
}

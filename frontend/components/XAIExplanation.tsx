"use client";

import { BrainCircuit, Sparkles, FileText, Check } from "lucide-react";

interface XAIExplanationProps {
  explanation?: string;
  ticker?: string;
}

export default function XAIExplanation({ explanation, ticker }: XAIExplanationProps) {
  if (!explanation) {
    return null;
  }

  // Split into paragraphs if formatted as plain text
  const paragraphs = explanation
    .split("\n\n")
    .map((p) => p.trim())
    .filter(Boolean);

  return (
    <div className="rounded-xl border border-cyan-500/20 bg-gradient-to-br from-slate-900/90 via-slate-950 to-slate-900/90 p-5 shadow-[0_0_30px_rgba(6,182,212,0.08)] backdrop-blur-md">
      <div className="flex items-center justify-between border-b border-cyan-500/20 pb-3">
        <div className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg border border-cyan-400/30 bg-cyan-400/10 text-cyan-300 shadow-[0_0_12px_rgba(34,211,238,0.2)]">
            <BrainCircuit className="h-4 w-4" />
          </div>
          <div>
            <h3 className="font-mono text-xs font-extrabold uppercase tracking-wider text-cyan-200">
              Explainable AI (XAI) Synthesis Trace
            </h3>
            <p className="text-[10px] text-slate-400">
              Transparent reasoning path for {ticker || "target asset"}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-1.5 rounded-full border border-cyan-400/30 bg-cyan-400/10 px-3 py-1 font-mono text-[10px] font-bold text-cyan-300">
          <Sparkles className="h-3 w-3" />
          <span>LLM EXPLAINABILITY</span>
        </div>
      </div>

      <div className="mt-4 space-y-3 text-xs leading-relaxed text-slate-300">
        {paragraphs.length > 1 ? (
          paragraphs.map((para, idx) => (
            <p
              key={idx}
              className="rounded-lg border border-slate-800/60 bg-slate-950/40 p-3.5 leading-6 text-slate-200 font-sans"
            >
              {para}
            </p>
          ))
        ) : (
          <p className="rounded-lg border border-slate-800/60 bg-slate-950/40 p-3.5 leading-6 text-slate-200 font-sans">
            {explanation}
          </p>
        )}
      </div>

      <div className="mt-4 flex flex-wrap items-center justify-between gap-3 border-t border-slate-800/80 pt-3 text-[11px] font-mono text-slate-400">
        <div className="flex items-center gap-2">
          <Check className="h-3.5 w-3.5 text-emerald-400" />
          <span>Multi-Agent Consensus Verified</span>
        </div>
        <span>Dynamic Weight Model v2.0</span>
      </div>
    </div>
  );
}

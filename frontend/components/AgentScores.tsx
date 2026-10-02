"use client";

import { Newspaper, CandlestickChart, ShieldAlert, Globe2, BarChart2, CheckCircle2 } from "lucide-react";

interface AgentContribution {
  agent: string;
  score: number;
  weight: number;
  weighted_score: number;
  confidence: number;
  key_factors: string[];
  summary: string;
}

interface AgentScoresProps {
  contributions?: AgentContribution[];
}

const AGENT_ICON_MAP: Record<string, any> = {
  news: Newspaper,
  technical: CandlestickChart,
  risk: ShieldAlert,
  macro: Globe2,
  fundamental: BarChart2,
};

export default function AgentScores({ contributions }: AgentScoresProps) {
  if (!contributions || contributions.length === 0) {
    return (
      <div className="rounded-xl border border-slate-800/90 bg-slate-900/40 p-4 text-center text-xs text-slate-500 font-mono">
        No agent breakdown available
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-2">
        <h3 className="font-mono text-xs font-semibold uppercase tracking-wider text-slate-200">
          Multi-Agent Score Breakdown
        </h3>
        <span className="font-mono text-[10px] text-slate-400">
          5 ACTIVE AGENTS
        </span>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
        {contributions.map((item) => {
          const Icon = AGENT_ICON_MAP[item.agent.toLowerCase()] || BarChart2;
          const isPositive = item.score > 0;
          const isNegative = item.score < 0;

          const scoreColor = isPositive
            ? "text-emerald-400"
            : isNegative
            ? "text-rose-400"
            : "text-amber-400";

          return (
            <div
              key={item.agent}
              className="flex flex-col justify-between rounded-xl border border-slate-800/90 bg-slate-900/60 p-3.5 backdrop-blur-sm transition hover:border-slate-700"
            >
              <div>
                <div className="flex items-center justify-between border-b border-slate-800/60 pb-2">
                  <div className="flex items-center gap-2">
                    <div className="flex h-7 w-7 items-center justify-center rounded-lg border border-cyan-500/20 bg-cyan-500/10 text-cyan-300">
                      <Icon className="h-4 w-4" />
                    </div>
                    <span className="font-mono text-xs font-bold capitalize text-slate-200">
                      {item.agent} Agent
                    </span>
                  </div>
                  <span className={`font-mono text-sm font-extrabold ${scoreColor}`}>
                    {item.score > 0 ? `+${item.score.toFixed(2)}` : item.score.toFixed(2)}
                  </span>
                </div>

                <div className="mt-2.5 flex items-center justify-between text-[11px] font-mono text-slate-400">
                  <span>Weight: {(item.weight * 100).toFixed(0)}%</span>
                  <span>Confidence: {(item.confidence * 100).toFixed(0)}%</span>
                </div>

                {item.key_factors && item.key_factors.length > 0 && (
                  <div className="mt-3 space-y-1">
                    {item.key_factors.slice(0, 3).map((factor, idx) => (
                      <div key={idx} className="flex items-start gap-1.5 text-[11px] text-slate-300">
                        <CheckCircle2 className="mt-0.5 h-3 w-3 shrink-0 text-cyan-400" />
                        <span className="line-clamp-2">{factor}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="mt-3 border-t border-slate-800/60 pt-2 text-[11px] leading-relaxed text-slate-400 line-clamp-3">
                {item.summary}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

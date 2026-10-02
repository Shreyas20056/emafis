"use client";

import { SlidersHorizontal, Newspaper, CandlestickChart, ShieldAlert, Globe2, BarChart2 } from "lucide-react";

interface AgentWeightsProps {
  weights?: Record<string, number>;
}

const AGENT_CONFIG: Record<string, { label: string; icon: any; color: string }> = {
  news: { label: "News Sentiment", icon: Newspaper, color: "from-blue-500 to-cyan-400" },
  technical: { label: "Technical Indicators", icon: CandlestickChart, color: "from-emerald-500 to-teal-400" },
  risk: { label: "Risk Assessment", icon: ShieldAlert, color: "from-rose-500 to-amber-400" },
  macro: { label: "Macro Environment", icon: Globe2, color: "from-purple-500 to-indigo-400" },
  fundamental: { label: "Fundamental Valuation", icon: BarChart2, color: "from-amber-500 to-yellow-400" },
};

export default function AgentWeights({ weights }: AgentWeightsProps) {
  const defaultWeights = {
    news: 0.20,
    technical: 0.25,
    risk: 0.20,
    macro: 0.15,
    fundamental: 0.20,
  };

  const activeWeights = weights || defaultWeights;

  return (
    <div className="rounded-xl border border-slate-800/90 bg-slate-900/40 p-4 shadow-[0_16px_40px_rgba(0,0,0,0.15)] backdrop-blur-sm">
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
        <div className="flex items-center gap-2">
          <SlidersHorizontal className="h-4 w-4 text-cyan-400" />
          <h3 className="font-mono text-xs font-semibold uppercase tracking-wider text-slate-200">
            Dynamic Agent Weights
          </h3>
        </div>
        <span className="rounded border border-cyan-400/20 bg-cyan-400/10 px-2 py-0.5 font-mono text-[9px] font-bold text-cyan-300">
          REGIME ADAPTIVE
        </span>
      </div>

      <div className="mt-4 space-y-3.5">
        {Object.entries(activeWeights).map(([agentKey, rawWeight]) => {
          const config = AGENT_CONFIG[agentKey.toLowerCase()] || {
            label: agentKey.toUpperCase(),
            icon: BarChart2,
            color: "from-cyan-500 to-blue-400",
          };
          const Icon = config.icon;
          const pct = Math.round((rawWeight || 0) * 100);

          return (
            <div key={agentKey} className="space-y-1">
              <div className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2 text-slate-300 font-medium">
                  <Icon className="h-3.5 w-3.5 text-cyan-400" />
                  <span>{config.label}</span>
                </div>
                <span className="font-mono text-xs font-bold text-cyan-300">
                  {pct}%
                </span>
              </div>
              <div className="h-2 w-full overflow-hidden rounded-full bg-slate-950">
                <div
                  className={`h-full rounded-full bg-gradient-to-r ${config.color} transition-all duration-500`}
                  style={{ width: `${pct}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

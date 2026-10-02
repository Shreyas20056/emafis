"use client";

import { ShieldCheck, Flame, Gauge, DollarSign, Activity } from "lucide-react";

interface RecommendationCardProps {
  action: string;
  confidence: number;
  weightedScore: number;
  marketRegime: string;
  price?: number | null;
  timestamp?: string;
}

export default function RecommendationCard({
  action,
  confidence,
  weightedScore,
  marketRegime,
  price,
  timestamp,
}: RecommendationCardProps) {
  const isBuy = action?.toUpperCase() === "BUY";
  const isSell = action?.toUpperCase() === "SELL";

  const actionColor = isBuy
    ? "bg-emerald-500/15 border-emerald-500/40 text-emerald-300 shadow-[0_0_25px_rgba(16,185,129,0.25)]"
    : isSell
    ? "bg-rose-500/15 border-rose-500/40 text-rose-300 shadow-[0_0_25px_rgba(244,63,94,0.25)]"
    : "bg-amber-500/15 border-amber-500/40 text-amber-300 shadow-[0_0_25px_rgba(245,158,11,0.25)]";

  const regimeFormatted = (marketRegime || "neutral")
    .replace(/_/g, " ")
    .toUpperCase();

  return (
    <div className="rounded-xl border border-slate-800/90 bg-gradient-to-br from-slate-900/80 to-slate-950/90 p-5 shadow-xl backdrop-blur-sm">
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
        <div className="flex items-center gap-2">
          <ShieldCheck className="h-4 w-4 text-cyan-400" />
          <h3 className="font-mono text-xs font-semibold uppercase tracking-wider text-slate-300">
            EMAFIS Consensus Signal
          </h3>
        </div>
        <span className="rounded border border-cyan-400/20 bg-cyan-400/10 px-2 py-0.5 font-mono text-[10px] font-bold text-cyan-300">
          AI VERDICT
        </span>
      </div>

      <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {/* Recommendation Badge */}
        <div className="flex flex-col justify-center rounded-xl border border-slate-800/80 bg-slate-950/40 p-4">
          <span className="font-mono text-[10px] uppercase tracking-wider text-slate-400">
            Final Recommendation
          </span>
          <div className="mt-2 flex items-center gap-2">
            <span
              className={`rounded-lg border px-4 py-1.5 font-mono text-xl font-extrabold tracking-wider ${actionColor}`}
            >
              {action || "ANALYZING"}
            </span>
          </div>
        </div>

        {/* Confidence Score */}
        <div className="flex flex-col justify-center rounded-xl border border-slate-800/80 bg-slate-950/40 p-4">
          <div className="flex items-center justify-between">
            <span className="font-mono text-[10px] uppercase tracking-wider text-slate-400">
              System Confidence
            </span>
            <Gauge className="h-4 w-4 text-cyan-400" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="font-mono text-2xl font-extrabold text-slate-100">
              {confidence ? confidence.toFixed(1) : "0.0"}%
            </span>
          </div>
          <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-slate-800">
            <div
              className="h-full rounded-full bg-gradient-to-r from-cyan-400 to-emerald-400 transition-all duration-500"
              style={{ width: `${Math.min(confidence || 0, 100)}%` }}
            />
          </div>
        </div>

        {/* Market Regime */}
        <div className="flex flex-col justify-center rounded-xl border border-slate-800/80 bg-slate-950/40 p-4">
          <div className="flex items-center justify-between">
            <span className="font-mono text-[10px] uppercase tracking-wider text-slate-400">
              Market Regime
            </span>
            <Activity className="h-4 w-4 text-amber-400" />
          </div>
          <span className="mt-2 font-mono text-sm font-bold text-amber-300">
            {regimeFormatted}
          </span>
          <span className="mt-1 text-[10px] text-slate-500">
            Adaptive weighting active
          </span>
        </div>

        {/* Weighted Score & Live Price */}
        <div className="flex flex-col justify-center rounded-xl border border-slate-800/80 bg-slate-950/40 p-4">
          <span className="font-mono text-[10px] uppercase tracking-wider text-slate-400">
            Consensus Score / Price
          </span>
          <div className="mt-2 flex items-baseline justify-between">
            <span className="font-mono text-lg font-extrabold text-slate-100">
              {weightedScore !== undefined ? (weightedScore > 0 ? `+${weightedScore.toFixed(3)}` : weightedScore.toFixed(3)) : "0.00"}
            </span>
            {price && (
              <span className="font-mono text-xs font-semibold text-cyan-400">
                ₹{price.toFixed(2)}
              </span>
            )}

          </div>
          <span className="mt-1 text-[10px] text-slate-500">
            Score range: -1.0 to +1.0
          </span>
        </div>
      </div>
    </div>
  );
}

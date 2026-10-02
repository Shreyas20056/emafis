"use client";

import { useState } from "react";
import {
  TrendingUp,
  TrendingDown,
  Plus,
  ArrowUpDown,
  Trash2,
  Edit2,
  Sparkles,
  PieChart,
  DollarSign
} from "lucide-react";

export interface Holding {
  ticker: string;
  quantity: number;
  avg_buy_price: number;
  current_price?: number;
  pnl_pct?: number;
  unrealized_pnl?: number;
  portfolio_action?: string;
  stock_action?: string;
  confidence?: number;
  xai_summary?: string;
}

interface PortfolioTableProps {
  holdings: Holding[];
  onAddHolding: () => void;
  onRecordTrade: (ticker?: string) => void;
  onEditHolding: (holding: Holding) => void;
  onDeleteHolding: (ticker: string) => void;
  onAnalyzePortfolio: () => void;
  isAnalyzing: boolean;
}

export default function PortfolioTable({
  holdings,
  onAddHolding,
  onRecordTrade,
  onEditHolding,
  onDeleteHolding,
  onAnalyzePortfolio,
  isAnalyzing,
}: PortfolioTableProps) {
  const getActionBadge = (action?: string) => {
    if (!action) return null;
    const act = action.toUpperCase();

    let bg = "bg-slate-800 text-slate-300 border-slate-700";
    if (["ACCUMULATE", "BUY_DIP", "STRONG_BUY", "BUY"].includes(act)) {
      bg = "bg-emerald-500/15 text-emerald-300 border-emerald-500/30 shadow-[0_0_12px_rgba(16,185,129,0.15)]";
    } else if (["TAKE_PROFIT", "REDUCE", "STOP_LOSS", "SELL", "EXIT"].includes(act)) {
      bg = "bg-rose-500/15 text-rose-300 border-rose-500/30 shadow-[0_0_12px_rgba(244,63,94,0.15)]";
    } else if (act === "HOLD") {
      bg = "bg-amber-500/15 text-amber-300 border-amber-500/30 shadow-[0_0_12px_rgba(245,158,11,0.15)]";
    }

    return (
      <span className={`inline-flex items-center rounded border px-2.5 py-1 font-mono text-[10px] font-extrabold tracking-wider ${bg}`}>
        {act.replace(/_/g, " ")}
      </span>
    );
  };

  return (
    <div className="rounded-xl border border-slate-800/90 bg-slate-900/40 shadow-[0_16px_40px_rgba(0,0,0,0.15)] backdrop-blur-sm overflow-hidden">
      {/* Table Header Controls */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800/80 p-4">
        <div className="flex items-center gap-2">
          <PieChart className="h-4 w-4 text-cyan-400" />
          <h3 className="font-mono text-xs font-semibold uppercase tracking-wider text-slate-200">
            Portfolio Positions ({holdings.length})
          </h3>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={onAddHolding}
            className="flex items-center gap-1.5 rounded-lg border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs font-medium text-slate-200 hover:border-slate-600 hover:bg-slate-700 transition"
          >
            <Plus className="h-3.5 w-3.5 text-cyan-400" />
            <span>Add Position</span>
          </button>

          <button
            onClick={() => onRecordTrade()}
            className="flex items-center gap-1.5 rounded-lg border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs font-medium text-slate-200 hover:border-slate-600 hover:bg-slate-700 transition"
          >
            <ArrowUpDown className="h-3.5 w-3.5 text-cyan-400" />
            <span>Record Trade</span>
          </button>

          <button
            onClick={onAnalyzePortfolio}
            disabled={isAnalyzing || holdings.length === 0}
            className="flex items-center gap-1.5 rounded-lg border border-cyan-500/30 bg-gradient-to-r from-cyan-500 to-blue-600 px-4 py-1.5 text-xs font-bold text-slate-950 hover:from-cyan-400 hover:to-blue-500 disabled:opacity-50 transition shadow-[0_0_15px_rgba(34,211,238,0.2)]"
          >
            <Sparkles className={`h-3.5 w-3.5 ${isAnalyzing ? "animate-spin" : ""}`} />
            <span>{isAnalyzing ? "Analyzing..." : "Analyze Portfolio"}</span>
          </button>
        </div>
      </div>

      {/* Table Content */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-slate-950/60 font-mono text-[10px] uppercase text-slate-400 border-b border-slate-800/80">
            <tr>
              <th className="px-4 py-3">Asset Ticker</th>
              <th className="px-4 py-3">Quantity</th>
              <th className="px-4 py-3">Avg Buy Price</th>
              <th className="px-4 py-3">Current Price</th>
              <th className="px-4 py-3">Unrealized P&L</th>
              <th className="px-4 py-3">AI Rebalancer Verdict</th>
              <th className="px-4 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 font-sans">
            {holdings.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-4 py-8 text-center text-slate-500 font-mono text-xs">
                  No holdings found. Click "Add Position" above to add your first stock.
                </td>
              </tr>
            ) : (
              holdings.map((h) => {
                const current = h.current_price || h.avg_buy_price;
                const pnl = h.unrealized_pnl !== undefined ? h.unrealized_pnl : (current - h.avg_buy_price) * h.quantity;
                const pnlPct = h.pnl_pct !== undefined ? h.pnl_pct : h.avg_buy_price > 0 ? ((current - h.avg_buy_price) / h.avg_buy_price) * 100 : 0;
                const isPos = pnl >= 0;

                return (
                  <tr key={h.ticker} className="hover:bg-slate-800/30 transition">
                    <td className="px-4 py-3 font-mono font-bold text-slate-100">
                      {h.ticker}
                    </td>
                    <td className="px-4 py-3 font-mono">{h.quantity}</td>
                    <td className="px-4 py-3 font-mono">₹{h.avg_buy_price.toFixed(2)}</td>
                    <td className="px-4 py-3 font-mono">
                      ₹{current.toFixed(2)}
                    </td>
                    <td className="px-4 py-3 font-mono">
                      <div className={`flex items-center gap-1 font-bold ${isPos ? "text-emerald-400" : "text-rose-400"}`}>
                        {isPos ? <TrendingUp className="h-3.5 w-3.5" /> : <TrendingDown className="h-3.5 w-3.5" />}
                        <span>
                          {isPos ? "+" : ""}₹{pnl.toFixed(2)} ({isPos ? "+" : ""}{pnlPct.toFixed(2)}%)
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      {getActionBadge(h.portfolio_action || h.stock_action)}
                    </td>

                    <td className="px-4 py-3 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => onEditHolding(h)}
                          className="rounded p-1 text-slate-400 hover:bg-slate-800 hover:text-cyan-300 transition"
                          title="Edit Position"
                        >
                          <Edit2 className="h-3.5 w-3.5" />
                        </button>
                        <button
                          onClick={() => onDeleteHolding(h.ticker)}
                          className="rounded p-1 text-slate-400 hover:bg-rose-500/10 hover:text-rose-300 transition"
                          title="Delete Position"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

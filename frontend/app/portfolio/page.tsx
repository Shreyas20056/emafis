"use client";

import { useState, useEffect } from "react";
import ProtectedRoute from "@/components/ProtectedRoute";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import PortfolioTable, { Holding } from "@/components/PortfolioTable";
import AddHoldingModal from "@/components/AddHoldingModal";
import TradeModal from "@/components/TradeModal";
import {
  getPortfolioApi,
  addHoldingApi,
  updateHoldingApi,
  deleteHoldingApi,
  recordTradeApi,
  analyzePortfolioApi
} from "@/lib/api";
import {
  PieChart,
  DollarSign,
  TrendingUp,
  TrendingDown,
  Sparkles,
  ShieldCheck,
  AlertCircle,
  RefreshCw
} from "lucide-react";

export default function PortfolioPage() {
  const [holdings, setHoldings] = useState<Holding[]>([]);
  const [summary, setSummary] = useState<{
    total_invested: number;
    current_value: number;
    overall_pnl: number;
    overall_pnl_pct: number;
  } | null>(null);

  const [isLoading, setIsLoading] = useState(true);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // Modals state
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [editingHolding, setEditingHolding] = useState<Holding | null>(null);
  const [isTradeModalOpen, setIsTradeModalOpen] = useState(false);
  const [tradeDefaultTicker, setTradeDefaultTicker] = useState("");

  const fetchPortfolio = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getPortfolioApi();
      if (data && data.holdings) {
        setHoldings(data.holdings);
      } else {
        setHoldings([]);
      }
    } catch (err: any) {
      console.error("Portfolio load error:", err);
      setError("Unable to connect to portfolio service");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchPortfolio();
  }, []);

  const handleAddOrUpdateHolding = async (data: { ticker: string; quantity: number; avg_buy_price: number }) => {
    if (editingHolding) {
      await updateHoldingApi(data.ticker, {
        quantity: data.quantity,
        avg_buy_price: data.avg_buy_price,
      });
      setSuccessMsg(`Successfully updated ${data.ticker}`);
    } else {
      await addHoldingApi(data);
      setSuccessMsg(`Successfully added ${data.ticker} to portfolio`);
    }
    await fetchPortfolio();
    setTimeout(() => setSuccessMsg(null), 4000);
  };

  const handleDeleteHolding = async (ticker: string) => {
    if (!confirm(`Are you sure you want to remove ${ticker} from your portfolio?`)) return;
    try {
      await deleteHoldingApi(ticker);
      setSuccessMsg(`Removed ${ticker} from portfolio`);
      await fetchPortfolio();
      setTimeout(() => setSuccessMsg(null), 4000);
    } catch (err: any) {
      setError(err.message || `Failed to delete ${ticker}`);
    }
  };

  const handleRecordTrade = async (trade: { ticker: string; action: "BUY" | "SELL"; quantity: number; price: number }) => {
    await recordTradeApi(trade);
    setSuccessMsg(`Successfully recorded ${trade.action} for ${trade.ticker}`);
    await fetchPortfolio();
    setTimeout(() => setSuccessMsg(null), 4000);
  };

  const handleAnalyzePortfolio = async () => {
    if (holdings.length === 0) return;
    setIsAnalyzing(true);
    setError(null);
    try {
      const result = await analyzePortfolioApi();
      if (result) {
        if (result.holdings) setHoldings(result.holdings);
        if (result.portfolio_summary) setSummary(result.portfolio_summary);
        setSuccessMsg("Multi-Agent Portfolio Rebalancing Complete!");
        setTimeout(() => setSuccessMsg(null), 4000);
      }
    } catch (err: any) {
      setError(err.message || "Failed to analyze portfolio");
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Compute local summary if server analysis hasn't run yet
  const totalInvested = summary ? summary.total_invested : holdings.reduce((sum, h) => sum + h.avg_buy_price * h.quantity, 0);
  const totalCurrent = summary ? summary.current_value : holdings.reduce((sum, h) => sum + (h.current_price || h.avg_buy_price) * h.quantity, 0);
  const overallPnL = summary ? summary.overall_pnl : totalCurrent - totalInvested;
  const overallPnLPct = summary ? summary.overall_pnl_pct : totalInvested > 0 ? (overallPnL / totalInvested) * 100 : 0;
  const isPositive = overallPnL >= 0;

  return (
    <ProtectedRoute>
      <div className="flex min-h-screen flex-col bg-[#0b0f17] text-slate-100 font-sans selection:bg-cyan-500/30 selection:text-cyan-200">
        <Navbar />

        <main className="mx-auto flex-1 w-full max-w-[1800px] px-4 py-6 lg:px-7 space-y-6">
          {/* Header Banner */}
          <div className="flex flex-wrap items-center justify-between gap-4 rounded-xl border border-slate-800/90 bg-slate-900/50 p-4 backdrop-blur-md">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-cyan-500/30 bg-cyan-500/10 text-cyan-300">
                <PieChart className="h-5 w-5" />
              </div>
              <div>
                <h1 className="font-mono text-sm font-extrabold uppercase tracking-wider text-slate-100">
                  Portfolio Intelligence & Rebalancing Console
                </h1>
                <p className="text-[11px] text-slate-400">
                  Manage holdings and run multi-agent position risk evaluations
                </p>
              </div>
            </div>
          </div>

          {error && (
            <div className="flex items-center gap-2 rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 text-xs font-mono text-rose-300">
              <AlertCircle className="h-4 w-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {successMsg && (
            <div className="flex items-center gap-2 rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-4 text-xs font-mono text-emerald-300">
              <ShieldCheck className="h-4 w-4 shrink-0" />
              <span>{successMsg}</span>
            </div>
          )}

          {/* Portfolio Summary Cards */}
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div className="rounded-xl border border-slate-800/90 bg-slate-900/40 p-4 backdrop-blur-sm">
              <span className="font-mono text-[10px] uppercase tracking-wider text-slate-400">
                Total Invested Capital
              </span>
              <p className="mt-2 font-mono text-2xl font-extrabold text-slate-100">
                ${totalInvested.toFixed(2)}
              </p>
              <span className="mt-1 text-[10px] text-slate-500">
                Combined cost basis
              </span>
            </div>

            <div className="rounded-xl border border-slate-800/90 bg-slate-900/40 p-4 backdrop-blur-sm">
              <span className="font-mono text-[10px] uppercase tracking-wider text-slate-400">
                Current Market Value
              </span>
              <p className="mt-2 font-mono text-2xl font-extrabold text-cyan-300">
                ${totalCurrent.toFixed(2)}
              </p>
              <span className="mt-1 text-[10px] text-slate-500">
                Live asset valuation
              </span>
            </div>

            <div className="rounded-xl border border-slate-800/90 bg-slate-900/40 p-4 backdrop-blur-sm">
              <span className="font-mono text-[10px] uppercase tracking-wider text-slate-400">
                Total Unrealized P&L
              </span>
              <div className={`mt-2 flex items-center gap-1 font-mono text-2xl font-extrabold ${isPositive ? "text-emerald-400" : "text-rose-400"}`}>
                {isPositive ? <TrendingUp className="h-5 w-5" /> : <TrendingDown className="h-5 w-5" />}
                <span>
                  {isPositive ? "+" : ""}${overallPnL.toFixed(2)}
                </span>
              </div>
              <span className={`mt-1 text-[10px] font-mono font-bold ${isPositive ? "text-emerald-400" : "text-rose-400"}`}>
                {isPositive ? "+" : ""}{overallPnLPct.toFixed(2)}% overall return
              </span>
            </div>

            <div className="rounded-xl border border-slate-800/90 bg-slate-900/40 p-4 backdrop-blur-sm">
              <span className="font-mono text-[10px] uppercase tracking-wider text-slate-400">
                Active Positions
              </span>
              <p className="mt-2 font-mono text-2xl font-extrabold text-slate-100">
                {holdings.length}
              </p>
              <span className="mt-1 text-[10px] text-slate-500">
                Assets in watchlist
              </span>
            </div>
          </div>

          {/* Holdings Table */}
          {isLoading ? (
            <div className="flex h-64 flex-col items-center justify-center rounded-xl border border-slate-800 bg-slate-900/40 text-slate-400">
              <RefreshCw className="h-8 w-8 animate-spin text-cyan-400" />
              <p className="mt-3 font-mono text-xs text-slate-300">Loading portfolio positions...</p>
            </div>
          ) : (
            <PortfolioTable
              holdings={holdings}
              onAddHolding={() => {
                setEditingHolding(null);
                setIsAddModalOpen(true);
              }}
              onRecordTrade={(ticker) => {
                setTradeDefaultTicker(ticker || "");
                setIsTradeModalOpen(true);
              }}
              onEditHolding={(holding) => {
                setEditingHolding(holding);
                setIsAddModalOpen(true);
              }}
              onDeleteHolding={handleDeleteHolding}
              onAnalyzePortfolio={handleAnalyzePortfolio}
              isAnalyzing={isAnalyzing}
            />
          )}

          {/* AI Rebalancing Explanations Section */}
          {holdings.some((h) => h.xai_summary) && (
            <div className="space-y-4 rounded-xl border border-slate-800/90 bg-slate-900/40 p-5">
              <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
                <Sparkles className="h-4 w-4 text-cyan-400" />
                <h3 className="font-mono text-xs font-semibold uppercase tracking-wider text-slate-200">
                  Position-Level Rebalancing Reasoning
                </h3>
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                {holdings
                  .filter((h) => h.xai_summary)
                  .map((h) => (
                    <div
                      key={h.ticker}
                      className="rounded-xl border border-slate-800 bg-slate-950/60 p-4 text-xs space-y-2"
                    >
                      <div className="flex items-center justify-between font-mono font-bold text-slate-200">
                        <span>{h.ticker}</span>
                        <span className="text-cyan-300">
                          {h.portfolio_action?.replace(/_/g, " ")}
                        </span>
                      </div>
                      <p className="text-slate-300 leading-relaxed text-[11px]">
                        {h.xai_summary}
                      </p>
                    </div>
                  ))}
              </div>
            </div>
          )}
        </main>

        <AddHoldingModal
          isOpen={isAddModalOpen}
          onClose={() => setIsAddModalOpen(false)}
          onSubmit={handleAddOrUpdateHolding}
          initialData={editingHolding}
        />

        <TradeModal
          isOpen={isTradeModalOpen}
          onClose={() => setIsTradeModalOpen(false)}
          onSubmit={handleRecordTrade}
          defaultTicker={tradeDefaultTicker}
        />

        <Footer />
      </div>
    </ProtectedRoute>
  );
}

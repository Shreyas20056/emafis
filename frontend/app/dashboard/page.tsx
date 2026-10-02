"use client";

import { useState, useEffect } from "react";
import ProtectedRoute from "@/components/ProtectedRoute";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import StockChart from "@/components/StockChart";
import RecommendationCard from "@/components/RecommendationCard";
import AgentWeights from "@/components/AgentWeights";
import AgentScores from "@/components/AgentScores";
import XAIExplanation from "@/components/XAIExplanation";
import { analyzeStockApi } from "@/lib/api";
import { Search, Sparkles, RefreshCw, Cpu, CheckCircle2, AlertCircle } from "lucide-react";

const QUICK_TICKERS = [
  "RELIANCE",
  "TCS",
  "INFY",
  "HDFCBANK",
  "ICICIBANK",
  "TATAMOTORS",
  "SBIN",
  "SUZLON",
  "ZOMATO",
  "CDSL",
];

export default function DashboardPage() {
  const [ticker, setTicker] = useState("RELIANCE");
  const [searchInput, setSearchInput] = useState("RELIANCE");
  const [analysisData, setAnalysisData] = useState<any>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleRunAnalysis = async (symbolToAnalyze: string) => {
    const target = symbolToAnalyze.trim().toUpperCase();
    if (!target) return;

    setTicker(target);
    setIsAnalyzing(true);
    setError(null);

    try {
      const result = await analyzeStockApi(target);
      setAnalysisData(result);
    } catch (err: any) {
      console.error("Analysis error:", err);
      setError(err.message || `Failed to run multi-agent analysis for ${target}`);
    } finally {
      setIsAnalyzing(false);
    }
  };

  useEffect(() => {
    handleRunAnalysis("RELIANCE");
  }, []);


  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchInput) {
      handleRunAnalysis(searchInput);
    }
  };

  return (
    <ProtectedRoute>
      <div className="flex min-h-screen flex-col bg-[#0b0f17] text-slate-100 font-sans selection:bg-cyan-500/30 selection:text-cyan-200">
        <Navbar />

        <main className="mx-auto flex-1 w-full max-w-[1800px] px-4 py-6 lg:px-7 space-y-6">
          {/* Header Controls & Search Bar */}
          <div className="flex flex-wrap items-center justify-between gap-4 rounded-xl border border-slate-800/90 bg-slate-900/50 p-4 backdrop-blur-md">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-cyan-500/30 bg-cyan-500/10 text-cyan-300">
                <Cpu className="h-5 w-5" />
              </div>
              <div>
                <h1 className="font-mono text-sm font-extrabold uppercase tracking-wider text-slate-100">
                  Multi-Agent Intelligence Console
                </h1>
                <p className="text-[11px] text-slate-400">
                  Target Asset: <span className="font-mono font-bold text-cyan-300">{ticker}</span>
                </p>
              </div>
            </div>

            {/* Search Input */}
            <form onSubmit={handleSearchSubmit} className="flex items-center gap-2 flex-1 max-w-md">
              <div className="relative flex-1">
                <Search className="absolute left-3.5 top-2.5 h-4 w-4 text-slate-400" />
                <input
                  type="text"
                  value={searchInput}
                  onChange={(e) => setSearchInput(e.target.value.toUpperCase())}
                  placeholder="Enter Ticker (e.g. RELIANCE, TCS, NVDA)..."
                  className="w-full rounded-xl border border-slate-800 bg-slate-950/80 pl-10 pr-4 py-2 font-mono text-xs text-slate-100 placeholder-slate-500 focus:border-cyan-500 focus:outline-none"
                />
              </div>
              <button
                type="submit"
                disabled={isAnalyzing}
                className="flex items-center gap-1.5 rounded-xl border border-cyan-500/30 bg-gradient-to-r from-cyan-500 to-blue-600 px-4 py-2 font-mono text-xs font-bold text-slate-950 hover:from-cyan-400 hover:to-blue-500 shadow-[0_0_15px_rgba(34,211,238,0.2)] disabled:opacity-50 transition"
              >
                {isAnalyzing ? (
                  <RefreshCw className="h-4 w-4 animate-spin" />
                ) : (
                  <Sparkles className="h-4 w-4" />
                )}
                <span>{isAnalyzing ? "Analyzing..." : "Analyze"}</span>
              </button>
            </form>

            {/* Quick Chips */}
            <div className="flex flex-wrap items-center gap-1.5">
              <span className="font-mono text-[10px] text-slate-500 mr-1 hidden lg:inline">
                QUICK ASSETS:
              </span>
              {QUICK_TICKERS.map((t) => (
                <button
                  key={t}
                  onClick={() => {
                    setSearchInput(t);
                    handleRunAnalysis(t);
                  }}
                  className={`rounded-md border px-2 py-1 font-mono text-[10px] font-bold transition ${
                    ticker === t
                      ? "border-cyan-500/40 bg-cyan-500/15 text-cyan-300"
                      : "border-slate-800 bg-slate-950/40 text-slate-400 hover:text-slate-200 hover:border-slate-700"
                  }`}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>

          {error && (
            <div className="flex items-center gap-2 rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 text-xs font-mono text-rose-300">
              <AlertCircle className="h-4 w-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Main Grid Section */}
          <div className="grid gap-6 lg:grid-cols-12">
            {/* Left Column (Chart & Overview) */}
            <div className="lg:col-span-7 space-y-6">
              <StockChart ticker={ticker} />

              {analysisData && (
                <AgentScores contributions={analysisData.agent_contributions} />
              )}
            </div>

            {/* Right Column (Verdict & Dynamic Weights) */}
            <div className="lg:col-span-5 space-y-6">
              {isAnalyzing ? (
                <div className="flex h-64 flex-col items-center justify-center rounded-xl border border-slate-800 bg-slate-900/40 p-6 text-center text-slate-400">
                  <RefreshCw className="h-8 w-8 animate-spin text-cyan-400" />
                  <p className="mt-3 font-mono text-xs font-semibold text-slate-300">
                    Executing 5 Specialized Agent Models...
                  </p>
                  <p className="mt-1 text-[11px] text-slate-500">
                    Computing News, Technical, Risk, Macro & Fundamental drivers for {ticker}
                  </p>
                </div>
              ) : (
                <>
                  <RecommendationCard
                    action={analysisData?.action || "HOLD"}
                    confidence={analysisData?.confidence || 0}
                    weightedScore={analysisData?.weighted_score || 0}
                    marketRegime={analysisData?.market_regime || "neutral"}
                    price={analysisData?.price_at_recommendation}
                    timestamp={analysisData?.timestamp}
                  />

                  <AgentWeights weights={analysisData?.dynamic_weights} />
                </>
              )}
            </div>
          </div>

          {/* Bottom Full XAI Explanation */}
          {analysisData?.xai_explanation && (
            <XAIExplanation
              explanation={analysisData.xai_explanation}
              ticker={ticker}
            />
          )}
        </main>

        <Footer />
      </div>
    </ProtectedRoute>
  );
}

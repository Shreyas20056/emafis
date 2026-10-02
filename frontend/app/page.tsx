"use client";

import Link from "next/link";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import {
  Cpu,
  BrainCircuit,
  SlidersHorizontal,
  ShieldCheck,
  TrendingUp,
  Newspaper,
  CandlestickChart,
  Globe2,
  BarChart2,
  ArrowRight,
  Sparkles,
  Zap,
  CheckCircle2
} from "lucide-react";

export default function LandingPage() {
  return (
    <div className="flex min-h-screen flex-col bg-[#0b0f17] text-slate-100 font-sans selection:bg-cyan-500/30 selection:text-cyan-200">
      <Navbar />

      {/* Hero Section */}
      <section className="relative overflow-hidden pt-16 pb-20 lg:pt-24 lg:pb-32">
        {/* Background glow effects */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 h-[450px] w-[700px] rounded-full bg-gradient-to-tr from-cyan-600/15 via-blue-600/10 to-emerald-500/15 blur-[120px] pointer-events-none" />

        <div className="mx-auto max-w-[1400px] px-4 lg:px-7 relative z-10">
          <div className="text-center max-w-3xl mx-auto space-y-6">
            <div className="inline-flex items-center gap-2 rounded-full border border-cyan-500/30 bg-cyan-500/10 px-4 py-1.5 font-mono text-xs font-bold text-cyan-300 shadow-[0_0_20px_rgba(34,211,238,0.2)]">
              <Sparkles className="h-4 w-4" />
              <span>NEXT-GEN AI EQUITY RESEARCH PLATFORM</span>
            </div>

            <h1 className="font-mono text-4xl font-extrabold tracking-tight sm:text-6xl text-slate-50 leading-tight">
              EMAFIS
            </h1>

            <p className="font-mono text-lg sm:text-xl font-semibold text-cyan-400">
              Explainable Multi-Agent Financial Intelligence System
            </p>

            <p className="text-base sm:text-lg text-slate-300 leading-relaxed max-w-2xl mx-auto font-sans">
              An advanced multi-agent framework combining <strong className="text-slate-100">Dynamic Regime Weighting</strong>, <strong className="text-slate-100">Adaptive Reinforcement Learning</strong>, and <strong className="text-slate-100">Transparent XAI Reasoning</strong> to deliver institutional-grade investment signals for global & Indian equities.
            </p>

            <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
              <Link
                href="/signup"
                className="flex items-center gap-2 rounded-xl border border-cyan-400/40 bg-gradient-to-r from-cyan-500 via-blue-600 to-indigo-600 px-7 py-3.5 text-sm font-bold text-slate-950 hover:from-cyan-400 hover:to-indigo-500 shadow-[0_0_25px_rgba(34,211,238,0.3)] transition-all hover:scale-[1.02]"
              >
                <span>Get Started Now</span>
                <ArrowRight className="h-4 w-4" />
              </Link>

              <Link
                href="/login"
                className="flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-900/90 px-7 py-3.5 text-sm font-semibold text-slate-200 hover:border-slate-600 hover:bg-slate-800 transition-all"
              >
                <span>Access Console</span>
              </Link>
            </div>
          </div>

          {/* Interactive Live Demo Preview Box */}
          <div className="mt-14 max-w-5xl mx-auto rounded-2xl border border-slate-800/90 bg-gradient-to-b from-slate-900/90 to-slate-950/95 p-6 shadow-2xl backdrop-blur-xl">
            <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-4">
              <div className="flex items-center gap-3">
                <span className="flex h-3 w-3 rounded-full bg-rose-500" />
                <span className="flex h-3 w-3 rounded-full bg-amber-500" />
                <span className="flex h-3 w-3 rounded-full bg-emerald-500" />
                <span className="font-mono text-xs text-slate-400 font-semibold ml-2">
                  EMAFIS Live Terminal Analysis Preview · Ticker: NVDA
                </span>
              </div>
              <span className="rounded border border-emerald-400/30 bg-emerald-400/10 px-3 py-1 font-mono text-xs font-bold text-emerald-300">
                RECOMMENDATION: STRONG BUY (+0.42)
              </span>
            </div>

            <div className="mt-6 grid gap-6 md:grid-cols-3">
              <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-4">
                <div className="flex items-center justify-between text-xs font-mono text-slate-400">
                  <span>Market Regime</span>
                  <Zap className="h-4 w-4 text-amber-400" />
                </div>
                <p className="mt-2 font-mono text-lg font-bold text-amber-300">
                  NEWS DRIVEN
                </p>
                <p className="mt-1 text-[11px] text-slate-500">
                  News Agent weight boosted +17%
                </p>
              </div>

              <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-4">
                <div className="flex items-center justify-between text-xs font-mono text-slate-400">
                  <span>Confidence Gauge</span>
                  <ShieldCheck className="h-4 w-4 text-cyan-400" />
                </div>
                <p className="mt-2 font-mono text-lg font-bold text-cyan-300">
                  88.4% CONFIDENCE
                </p>
                <p className="mt-1 text-[11px] text-slate-500">
                  High agent consensus agreement
                </p>
              </div>

              <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-4">
                <div className="flex items-center justify-between text-xs font-mono text-slate-400">
                  <span>Top Active Agent</span>
                  <BrainCircuit className="h-4 w-4 text-emerald-400" />
                </div>
                <p className="mt-2 font-mono text-lg font-bold text-emerald-300">
                  TECHNICAL (Score +0.75)
                </p>
                <p className="mt-1 text-[11px] text-slate-500">
                  MACD Bullish Crossover & RSI 58
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section id="features" className="py-20 bg-slate-950/60 border-t border-slate-800/80">
        <div className="mx-auto max-w-[1400px] px-4 lg:px-7">
          <div className="text-center max-w-2xl mx-auto space-y-3 mb-14">
            <span className="font-mono text-xs font-bold text-cyan-400 tracking-widest uppercase">
              RESEARCH ARCHITECTURE
            </span>
            <h2 className="font-mono text-3xl font-extrabold text-slate-100">
              Why EMAFIS Outperforms Traditional Models
            </h2>
            <p className="text-sm text-slate-400">
              By deploying specialized domain agents with dynamic weight adaptation, EMAFIS eliminates single-model bias.
            </p>
          </div>

          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            {/* Feature 1 */}
            <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6 backdrop-blur-sm transition hover:border-cyan-500/40">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl border border-cyan-500/30 bg-cyan-500/10 text-cyan-300 mb-5">
                <Cpu className="h-6 w-6" />
              </div>
              <h3 className="font-mono text-base font-bold text-slate-100 mb-2">
                5 Specialized Agents
              </h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Dedicated News, Technical, Risk, Macro, and Fundamental agents analyzing market signals simultaneously.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6 backdrop-blur-sm transition hover:border-cyan-500/40">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl border border-amber-500/30 bg-amber-500/10 text-amber-300 mb-5">
                <SlidersHorizontal className="h-6 w-6" />
              </div>
              <h3 className="font-mono text-base font-bold text-slate-100 mb-2">
                Dynamic Regime Weighting
              </h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Automatically adjusts agent weights based on detected market regime (High Volatility, News-Driven, Trending).
              </p>
            </div>

            {/* Feature 3 */}
            <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6 backdrop-blur-sm transition hover:border-cyan-500/40">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl border border-emerald-500/30 bg-emerald-500/10 text-emerald-300 mb-5">
                <BrainCircuit className="h-6 w-6" />
              </div>
              <h3 className="font-mono text-base font-bold text-slate-100 mb-2">
                Explainable AI (XAI)
              </h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Generates clear, human-readable explanations outlining why a recommendation was reached with zero black boxes.
              </p>
            </div>

            {/* Feature 4 */}
            <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6 backdrop-blur-sm transition hover:border-cyan-500/40">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl border border-indigo-500/30 bg-indigo-500/10 text-indigo-300 mb-5">
                <TrendingUp className="h-6 w-6" />
              </div>
              <h3 className="font-mono text-base font-bold text-slate-100 mb-2">
                Portfolio Rebalancing
              </h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Contextual portfolio intelligence recommending Accumulate, Buy Dip, Take Profit, and Stop Loss actions.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 relative overflow-hidden">
        <div className="mx-auto max-w-[1200px] px-4 lg:px-7">
          <div className="rounded-2xl border border-cyan-500/30 bg-gradient-to-r from-slate-900 via-slate-950 to-slate-900 p-10 text-center shadow-2xl relative">
            <h2 className="font-mono text-3xl font-extrabold text-slate-100 mb-4">
              Ready to Upgrade Your Financial Intelligence?
            </h2>
            <p className="text-sm text-slate-400 max-w-xl mx-auto mb-8">
              Experience research-grade multi-agent stock analysis and explainable portfolio rebalancing today.
            </p>
            <Link
              href="/signup"
              className="inline-flex items-center gap-2 rounded-xl border border-cyan-400/40 bg-gradient-to-r from-cyan-500 to-blue-600 px-8 py-3.5 text-sm font-bold text-slate-950 hover:from-cyan-400 hover:to-blue-500 shadow-[0_0_25px_rgba(34,211,238,0.3)] transition"
            >
              <span>Create Free Account</span>
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}

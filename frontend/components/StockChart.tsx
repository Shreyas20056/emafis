"use client";

import { useState, useEffect } from "react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Bar,
  ComposedChart
} from "recharts";
import { getChartDataApi } from "@/lib/api";
import { CandlestickChart, TrendingUp, TrendingDown, RefreshCw } from "lucide-react";

interface StockChartProps {
  ticker: string;
}

export default function StockChart({ ticker }: StockChartProps) {
  const [period, setPeriod] = useState("3mo");
  const [data, setData] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchChart() {
      setIsLoading(true);
      setError(null);
      try {
        const res = await getChartDataApi(ticker, period);
        if (res && res.candles) {
          setData(res.candles);
        } else {
          setData([]);
        }
      } catch (err: any) {
        console.warn("Chart data error:", err);
        setError("Unable to load price history");
      } finally {
        setIsLoading(false);
      }
    }
    fetchChart();
  }, [ticker, period]);

  const periods = [
    { label: "1M", value: "1mo" },
    { label: "3M", value: "3mo" },
    { label: "6M", value: "6mo" },
    { label: "1Y", value: "1y" },
  ];

  const firstPrice = data.length > 0 ? data[0].close : 0;
  const lastPrice = data.length > 0 ? data[data.length - 1].close : 0;
  const priceChange = lastPrice - firstPrice;
  const priceChangePct = firstPrice > 0 ? (priceChange / firstPrice) * 100 : 0;
  const isPositive = priceChange >= 0;

  return (
    <div className="rounded-xl border border-slate-800/90 bg-slate-900/40 p-4 shadow-[0_16px_40px_rgba(0,0,0,0.15)] backdrop-blur-sm">
      {/* Chart Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-800/80">
        <div>
          <div className="flex items-center gap-2">
            <CandlestickChart className="h-4 w-4 text-cyan-400" />
            <h3 className="font-mono text-xs font-semibold uppercase tracking-wider text-slate-200">
              {ticker} Market Price Chart
            </h3>
          </div>
          {data.length > 0 && (
            <div className="mt-1 flex items-baseline gap-2">
              <span className="font-mono text-xl font-bold text-slate-100">
                ₹{lastPrice.toFixed(2)}
              </span>
              <span
                className={`flex items-center font-mono text-xs font-semibold ${
                  isPositive ? "text-emerald-400" : "text-rose-400"
                }`}
              >
                {isPositive ? (
                  <TrendingUp className="mr-0.5 h-3.5 w-3.5" />
                ) : (
                  <TrendingDown className="mr-0.5 h-3.5 w-3.5" />
                )}
                {isPositive ? "+" : ""}
                ₹{priceChange.toFixed(2)} ({isPositive ? "+" : ""}
                {priceChangePct.toFixed(2)}%)
              </span>
            </div>

          )}
        </div>

        {/* Period Selector */}
        <div className="flex items-center gap-1 rounded-lg border border-slate-800 bg-slate-950/60 p-1">
          {periods.map((p) => (
            <button
              key={p.value}
              onClick={() => setPeriod(p.value)}
              className={`rounded px-2.5 py-1 font-mono text-[11px] font-semibold transition ${
                period === p.value
                  ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/30"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      {/* Chart Body */}
      <div className="mt-4 h-[320px] w-full">
        {isLoading ? (
          <div className="flex h-full items-center justify-center text-slate-500">
            <RefreshCw className="h-6 w-6 animate-spin text-cyan-400" />
            <span className="ml-2 font-mono text-xs">Fetching candle data...</span>
          </div>
        ) : error || data.length === 0 ? (
          <div className="flex h-full items-center justify-center font-mono text-xs text-slate-500">
            {error || "No chart data available for this ticker"}
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="colorClose" x1="0" y1="0" x2="0" y2="1">
                  <stop
                    offset="5%"
                    stopColor={isPositive ? "#10b981" : "#f43f5e"}
                    stopOpacity={0.35}
                  />
                  <stop
                    offset="95%"
                    stopColor={isPositive ? "#10b981" : "#f43f5e"}
                    stopOpacity={0.0}
                  />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis
                dataKey="time"
                tick={{ fill: "#64748b", fontSize: 10 }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                domain={["auto", "auto"]}
                tick={{ fill: "#64748b", fontSize: 10 }}
                axisLine={false}
                tickLine={false}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#0f172a",
                  borderColor: "#334155",
                  borderRadius: "8px",
                  fontSize: "12px",
                  color: "#e2e8f0",
                }}
                formatter={(value: any) => [`₹${Number(value).toFixed(2)}`, "Close Price"]}
              />

              <Area
                type="monotone"
                dataKey="close"
                stroke={isPositive ? "#10b981" : "#f43f5e"}
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#colorClose)"
              />
            </ComposedChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}

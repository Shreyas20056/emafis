"use client";

import { useState } from "react";
import { X, ArrowUpDown } from "lucide-react";

interface TradeModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (trade: { ticker: string; action: "BUY" | "SELL"; quantity: number; price: number }) => Promise<void>;
  defaultTicker?: string;
}

export default function TradeModal({
  isOpen,
  onClose,
  onSubmit,
  defaultTicker = "",
}: TradeModalProps) {
  const [ticker, setTicker] = useState(defaultTicker);
  const [action, setAction] = useState<"BUY" | "SELL">("BUY");
  const [quantity, setQuantity] = useState("");
  const [price, setPrice] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const parsedQty = parseFloat(quantity);
    const parsedPrice = parseFloat(price);

    if (!ticker.trim()) {
      setError("Please enter a ticker symbol");
      return;
    }
    if (isNaN(parsedQty) || parsedQty <= 0) {
      setError("Quantity must be greater than 0");
      return;
    }
    if (isNaN(parsedPrice) || parsedPrice <= 0) {
      setError("Execution price must be greater than 0");
      return;
    }

    setIsSubmitting(true);
    try {
      await onSubmit({
        ticker: ticker.trim().toUpperCase(),
        action,
        quantity: parsedQty,
        price: parsedPrice,
      });
      onClose();
    } catch (err: any) {
      setError(err.message || "Failed to record trade");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 p-4 backdrop-blur-sm animate-in">
      <div className="w-full max-w-md rounded-xl border border-slate-800 bg-slate-900 p-6 shadow-2xl">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center gap-2">
            <ArrowUpDown className="h-4 w-4 text-cyan-400" />
            <h3 className="font-mono text-sm font-bold uppercase tracking-wider text-slate-100">
              Record Buy / Sell Trade
            </h3>
          </div>
          <button onClick={onClose} className="rounded text-slate-400 hover:text-slate-200">
            <X className="h-5 w-5" />
          </button>
        </div>

        {error && (
          <div className="mt-4 rounded-lg border border-rose-500/30 bg-rose-500/10 p-3 text-xs text-rose-300">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="mt-4 space-y-4">
          <div>
            <label className="block font-mono text-[11px] uppercase tracking-wider text-slate-400 mb-1">
              Trade Action
            </label>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => setAction("BUY")}
                className={`rounded-lg py-2 font-mono text-xs font-bold transition border ${
                  action === "BUY"
                    ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/50 shadow-[0_0_12px_rgba(16,185,129,0.2)]"
                    : "bg-slate-950 text-slate-400 border-slate-800"
                }`}
              >
                BUY
              </button>
              <button
                type="button"
                onClick={() => setAction("SELL")}
                className={`rounded-lg py-2 font-mono text-xs font-bold transition border ${
                  action === "SELL"
                    ? "bg-rose-500/20 text-rose-300 border-rose-500/50 shadow-[0_0_12px_rgba(244,63,94,0.2)]"
                    : "bg-slate-950 text-slate-400 border-slate-800"
                }`}
              >
                SELL
              </button>
            </div>
          </div>

          <div>
            <label className="block font-mono text-[11px] uppercase tracking-wider text-slate-400 mb-1">
              Stock Ticker Symbol
            </label>
            <input
              type="text"
              value={ticker}
              onChange={(e) => setTicker(e.target.value.toUpperCase())}
              placeholder="TCS / RELIANCE / NVDA"
              className="w-full rounded-lg border border-slate-800 bg-slate-950 px-3.5 py-2 font-mono text-xs text-slate-100 placeholder-slate-600 focus:border-cyan-500 focus:outline-none"
            />
          </div>

          <div>
            <label className="block font-mono text-[11px] uppercase tracking-wider text-slate-400 mb-1">
              Quantity / Shares
            </label>
            <input
              type="number"
              step="any"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              placeholder="5"
              className="w-full rounded-lg border border-slate-800 bg-slate-950 px-3.5 py-2 font-mono text-xs text-slate-100 placeholder-slate-600 focus:border-cyan-500 focus:outline-none"
            />
          </div>

          <div>
            <label className="block font-mono text-[11px] uppercase tracking-wider text-slate-400 mb-1">
              Executed Trade Price (₹ INR)
            </label>
            <input
              type="number"
              step="any"
              value={price}
              onChange={(e) => setPrice(e.target.value)}
              placeholder="2450.00"
              className="w-full rounded-lg border border-slate-800 bg-slate-950 px-3.5 py-2 font-mono text-xs text-slate-100 placeholder-slate-600 focus:border-cyan-500 focus:outline-none"
            />
          </div>


          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg border border-slate-800 bg-slate-950 px-4 py-2 text-xs font-medium text-slate-400 hover:text-slate-200"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="rounded-lg border border-cyan-500/30 bg-gradient-to-r from-cyan-500 to-blue-600 px-5 py-2 text-xs font-bold text-slate-950 hover:from-cyan-400 hover:to-blue-500 disabled:opacity-50"
            >
              {isSubmitting ? "Recording..." : `Execute ${action}`}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

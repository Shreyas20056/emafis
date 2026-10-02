"use client";

import { useState, useEffect } from "react";
import { X, Plus, Edit2 } from "lucide-react";
import { Holding } from "./PortfolioTable";

interface AddHoldingModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: { ticker: string; quantity: number; avg_buy_price: number }) => Promise<void>;
  initialData?: Holding | null;
}

export default function AddHoldingModal({
  isOpen,
  onClose,
  onSubmit,
  initialData,
}: AddHoldingModalProps) {
  const [ticker, setTicker] = useState("");
  const [quantity, setQuantity] = useState("");
  const [avgBuyPrice, setAvgBuyPrice] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (initialData) {
      setTicker(initialData.ticker);
      setQuantity(initialData.quantity.toString());
      setAvgBuyPrice(initialData.avg_buy_price.toString());
    } else {
      setTicker("");
      setQuantity("");
      setAvgBuyPrice("");
    }
    setError(null);
  }, [initialData, isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const parsedQty = parseFloat(quantity);
    const parsedPrice = parseFloat(avgBuyPrice);

    if (!ticker.trim()) {
      setError("Please enter a valid stock ticker symbol");
      return;
    }
    if (isNaN(parsedQty) || parsedQty <= 0) {
      setError("Quantity must be greater than 0");
      return;
    }
    if (isNaN(parsedPrice) || parsedPrice <= 0) {
      setError("Average buy price must be greater than 0");
      return;
    }

    setIsSubmitting(true);
    try {
      await onSubmit({
        ticker: ticker.trim().toUpperCase(),
        quantity: parsedQty,
        avg_buy_price: parsedPrice,
      });
      onClose();
    } catch (err: any) {
      setError(err.message || "Failed to save position");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 p-4 backdrop-blur-sm animate-in">
      <div className="w-full max-w-md rounded-xl border border-slate-800 bg-slate-900 p-6 shadow-2xl">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center gap-2">
            {initialData ? <Edit2 className="h-4 w-4 text-cyan-400" /> : <Plus className="h-4 w-4 text-cyan-400" />}
            <h3 className="font-mono text-sm font-bold uppercase tracking-wider text-slate-100">
              {initialData ? "Edit Position" : "Add Portfolio Position"}
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
              Stock Ticker (e.g. RELIANCE, TCS, NVDA)
            </label>
            <input
              type="text"
              disabled={!!initialData}
              value={ticker}
              onChange={(e) => setTicker(e.target.value.toUpperCase())}
              placeholder="NVDA / RELIANCE"
              className="w-full rounded-lg border border-slate-800 bg-slate-950 px-3.5 py-2 font-mono text-xs text-slate-100 placeholder-slate-600 focus:border-cyan-500 focus:outline-none disabled:opacity-60"
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
              placeholder="10"
              className="w-full rounded-lg border border-slate-800 bg-slate-950 px-3.5 py-2 font-mono text-xs text-slate-100 placeholder-slate-600 focus:border-cyan-500 focus:outline-none"
            />
          </div>

          <div>
            <label className="block font-mono text-[11px] uppercase tracking-wider text-slate-400 mb-1">
              Avg Buy Price ($ / ₹)
            </label>
            <input
              type="number"
              step="any"
              value={avgBuyPrice}
              onChange={(e) => setAvgBuyPrice(e.target.value)}
              placeholder="120.50"
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
              {isSubmitting ? "Saving..." : initialData ? "Update Position" : "Add Position"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

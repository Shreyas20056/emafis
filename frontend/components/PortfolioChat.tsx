"use client";

import { useState, useRef, useEffect } from "react";
import { MessageSquare, Send, Sparkles, Bot, User, RefreshCw, ChevronDown, ChevronUp, Trash2 } from "lucide-react";
import { chatPortfolioApi, getPortfolioChatHistoryApi, clearPortfolioChatHistoryApi } from "@/lib/api";


interface ChatMessage {
  sender: "user" | "ai";
  text: string;
  timestamp: string;
}

export default function PortfolioChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    async function loadHistory() {
      try {
        const res = await getPortfolioChatHistoryApi();
        if (res && res.messages && res.messages.length > 0) {
          setMessages(res.messages);
        } else {
          setMessages([
            {
              sender: "ai",
              text: "Namaste! I am your EMAFIS Real-Time Portfolio Chat Advisor. Ask me anything about your Indian stock positions (NIFTY 50 / SmallCap), asset allocation, dip buying, or risk strategy!",
              timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            },
          ]);
        }
      } catch (err) {
        console.warn("Could not load chat history:", err);
      }
    }
    loadHistory();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleClearHistory = async () => {
    if (!confirm("Clear portfolio chat history?")) return;
    try {
      await clearPortfolioChatHistoryApi();
      setMessages([
        {
          sender: "ai",
          text: "Chat history cleared. How can I assist with your portfolio strategy today?",
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    } catch (err) {
      console.error("Failed to clear chat:", err);
    }
  };


  const handleSend = async (textToSend?: string) => {
    const msg = (textToSend || input).trim();
    if (!msg || isLoading) return;

    const userMsg: ChatMessage = {
      sender: "user",
      text: msg,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!textToSend) setInput("");
    setIsLoading(true);

    try {
      const res = await chatPortfolioApi(msg);
      const aiMsg: ChatMessage = {
        sender: "ai",
        text: res.reply || "I analyzed your portfolio requirements. Consider staggered buying on market pullbacks.",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, aiMsg]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          sender: "ai",
          text: `Advisor error: ${err.message || "Could not reach portfolio advisor."}`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const samplePrompts = [
    "Should I buy the dip on RELIANCE or TCS?",
    "How is my portfolio risk exposure against NIFTY 50?",
    "Suggest profit-taking targets for my current holdings.",
  ];

  return (
    <div className="rounded-xl border border-cyan-500/30 bg-slate-900/60 shadow-[0_16px_40px_rgba(0,0,0,0.25)] backdrop-blur-md overflow-hidden">
      {/* Header Bar */}
      <div className="flex items-center justify-between border-b border-slate-800 bg-slate-950/80 px-4 py-3">
        <div className="flex items-center gap-2.5">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg border border-cyan-500/30 bg-cyan-500/10 text-cyan-300">
            <Bot className="h-4 w-4" />
          </div>
          <div>
            <h3 className="font-mono text-xs font-bold uppercase tracking-wider text-slate-100 flex items-center gap-2">
              <span>Real-Time Portfolio AI Advisor</span>
              <span className="flex items-center gap-1 text-[9px] text-emerald-400 font-normal">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
                ONLINE
              </span>
            </h3>
            <p className="text-[10px] text-slate-400">
              Personalized SEBI-Style Equity Strategy & Dip Planning
            </p>
          </div>
        </div>

        <div className="flex items-center gap-1">
          <button
            onClick={handleClearHistory}
            title="Clear Chat History"
            className="rounded p-1 text-slate-400 hover:bg-slate-800 hover:text-rose-400 transition"
          >
            <Trash2 className="h-4 w-4" />
          </button>
          <button
            onClick={() => setIsMinimized(!isMinimized)}
            className="rounded p-1 text-slate-400 hover:bg-slate-800 hover:text-slate-200 transition"
          >
            {isMinimized ? <ChevronDown className="h-4 w-4" /> : <ChevronUp className="h-4 w-4" />}
          </button>
        </div>

      </div>

      {!isMinimized && (
        <div className="flex flex-col h-[380px]">
          {/* Chat Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3 font-sans text-xs">
            {messages.map((m, idx) => (
              <div
                key={idx}
                className={`flex gap-2.5 ${m.sender === "user" ? "justify-end" : "justify-start"}`}
              >
                {m.sender === "ai" && (
                  <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg border border-cyan-500/30 bg-cyan-500/10 text-cyan-300">
                    <Bot className="h-3.5 w-3.5" />
                  </div>
                )}
                <div
                  className={`max-w-[80%] rounded-xl px-3.5 py-2.5 leading-relaxed shadow-sm ${
                    m.sender === "user"
                      ? "bg-gradient-to-r from-cyan-600 to-blue-600 text-slate-950 font-semibold"
                      : "border border-slate-800 bg-slate-950/80 text-slate-200"
                  }`}
                >
                  <p>{m.text}</p>
                  <span className={`block mt-1 text-[9px] font-mono ${m.sender === "user" ? "text-slate-900/70" : "text-slate-500"}`}>
                    {m.timestamp}
                  </span>
                </div>
                {m.sender === "user" && (
                  <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg border border-slate-700 bg-slate-800 text-slate-300 font-mono text-xs font-bold">
                    <User className="h-3.5 w-3.5" />
                  </div>
                )}
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start gap-2.5">
                <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg border border-cyan-500/30 bg-cyan-500/10 text-cyan-300">
                  <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                </div>
                <div className="rounded-xl border border-slate-800 bg-slate-950/80 px-3.5 py-2 text-slate-400 font-mono text-[11px]">
                  Portfolio AI is evaluating market positions & risk metrics...
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          {/* Quick Prompts */}
          <div className="flex flex-wrap items-center gap-1.5 px-4 py-2 border-t border-slate-800/60 bg-slate-950/40">
            <span className="font-mono text-[9px] text-slate-500 mr-1">SUGGESTIONS:</span>
            {samplePrompts.map((p, i) => (
              <button
                key={i}
                onClick={() => handleSend(p)}
                className="rounded-full border border-slate-800 bg-slate-900 px-2.5 py-1 text-[10px] text-slate-300 hover:border-cyan-500/40 hover:text-cyan-300 transition"
              >
                {p}
              </button>
            ))}
          </div>

          {/* Input Box */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="flex items-center gap-2 border-t border-slate-800 bg-slate-950/90 p-3"
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask AI advisor about RELIANCE, TCS, SmallCap allocations or exit points..."
              className="flex-1 rounded-xl border border-slate-800 bg-slate-900 px-3.5 py-2 font-sans text-xs text-slate-100 placeholder-slate-500 focus:border-cyan-500 focus:outline-none"
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="flex h-9 w-9 items-center justify-center rounded-xl border border-cyan-500/30 bg-gradient-to-r from-cyan-500 to-blue-600 text-slate-950 hover:from-cyan-400 hover:to-blue-500 disabled:opacity-40 transition"
            >
              <Send className="h-4 w-4" />
            </button>
          </form>
        </div>
      )}
    </div>
  );
}

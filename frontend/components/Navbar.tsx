"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import { Cpu, LayoutDashboard, PieChart, LogOut, User, Sparkles, ShieldCheck } from "lucide-react";

export default function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, isAuthenticated, logout } = useAuth();

  const handleLogout = () => {
    logout();
    router.push("/");
  };

  const navItemClass = (path: string) =>
    `flex items-center gap-2 rounded-lg px-3 py-1.5 text-xs font-medium transition-colors ${
      pathname === path
        ? "bg-cyan-500/10 text-cyan-300 border border-cyan-500/20 shadow-[0_0_12px_rgba(34,211,238,0.15)]"
        : "text-slate-400 hover:bg-slate-800/60 hover:text-slate-200"
    }`;

  return (
    <header className="sticky top-0 z-50 border-b border-slate-800/80 bg-[#0b0f17]/90 backdrop-blur-md">
      <div className="mx-auto flex max-w-[1800px] items-center justify-between px-4 py-3 lg:px-7">
        {/* Brand */}
        <Link href="/" className="flex items-center gap-3 group">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl border border-cyan-500/30 bg-cyan-500/10 text-cyan-400 shadow-[0_0_15px_rgba(34,211,238,0.2)] transition-transform group-hover:scale-105">
            <Cpu className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-base font-extrabold tracking-wider text-slate-100">
                EMAFIS
              </span>
              <span className="rounded bg-cyan-400/10 px-1.5 py-0.5 font-mono text-[9px] font-bold text-cyan-300 border border-cyan-400/20">
                v2.0 XAI
              </span>
            </div>
            <p className="text-[10px] text-slate-400 hidden sm:block">
              Multi-Agent Financial Intelligence
            </p>
          </div>
        </Link>

        {/* Navigation Links */}
        <nav className="flex items-center gap-2">
          {isAuthenticated ? (
            <>
              <Link href="/dashboard" className={navItemClass("/dashboard")}>
                <LayoutDashboard className="h-4 w-4" />
                <span>Dashboard</span>
              </Link>
              <Link href="/portfolio" className={navItemClass("/portfolio")}>
                <PieChart className="h-4 w-4" />
                <span>Portfolio</span>
              </Link>
            </>
          ) : (
            <>
              <Link href="/#features" className="hidden text-xs text-slate-400 hover:text-slate-200 md:block px-3">
                Architecture
              </Link>
              <Link href="/#xai" className="hidden text-xs text-slate-400 hover:text-slate-200 md:block px-3">
                XAI System
              </Link>
            </>
          )}
        </nav>

        {/* User Auth Controls */}
        <div className="flex items-center gap-3">
          {isAuthenticated ? (
            <div className="flex items-center gap-3">
              <div className="hidden sm:flex flex-col text-right">
                <span className="text-xs font-semibold text-slate-200">{user?.name}</span>
                <span className="text-[10px] text-slate-400 font-mono">{user?.email}</span>
              </div>
              <div className="flex h-8 w-8 items-center justify-center rounded-full border border-slate-700 bg-slate-800 text-cyan-300 font-mono text-xs font-bold shadow-inner">
                {user?.name ? user.name.slice(0, 2).toUpperCase() : "US"}
              </div>
              <button
                onClick={handleLogout}
                className="flex items-center gap-1.5 rounded-lg border border-slate-800 bg-slate-900/80 px-2.5 py-1.5 text-xs text-slate-400 hover:border-rose-500/30 hover:bg-rose-500/10 hover:text-rose-300 transition-all"
                title="Log Out"
              >
                <LogOut className="h-3.5 w-3.5" />
                <span className="hidden sm:inline">Logout</span>
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Link
                href="/login"
                className="rounded-lg border border-slate-800 bg-slate-900 px-3.5 py-1.5 text-xs font-medium text-slate-300 hover:border-slate-700 hover:bg-slate-800 hover:text-white transition"
              >
                Log In
              </Link>
              <Link
                href="/signup"
                className="flex items-center gap-1.5 rounded-lg border border-cyan-500/30 bg-gradient-to-r from-cyan-500 to-blue-600 px-3.5 py-1.5 text-xs font-bold text-slate-950 hover:from-cyan-400 hover:to-blue-500 shadow-[0_0_15px_rgba(34,211,238,0.25)] transition"
              >
                <Sparkles className="h-3.5 w-3.5" />
                <span>Get Started</span>
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

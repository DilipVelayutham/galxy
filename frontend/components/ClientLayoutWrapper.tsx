"use client";

import React from "react";
import { useAuth } from "@/context/AuthContext";
import { usePathname } from "next/navigation";
import Link from "next/link";
import { ShoppingBag, LogOut, ClipboardList, User } from "lucide-react";

export default function ClientLayoutWrapper({ children }: { children: React.ReactNode }) {
  const { user, logout } = useAuth();
  const pathname = usePathname();

  const isLogin = pathname === "/login";

  if (isLogin) {
    return <main>{children}</main>;
  }

  return (
    <div className="min-h-screen flex flex-col justify-between">
      {/* Dynamic Header Navbar */}
      <header className="sticky top-0 z-40 w-full glass-panel border-b border-white/5 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          {/* Logo brand */}
          <Link href="/checkout" className="flex items-center gap-2 group">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center shadow-lg shadow-indigo-500/20 group-hover:scale-105 transition-transform duration-200">
              <ShoppingBag className="h-5 w-5 text-white" />
            </div>
            <span className="font-extrabold text-lg tracking-wider bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent uppercase">
              Aura <span className="text-indigo-400">Design</span>
            </span>
          </Link>

          {/* Nav links and actions */}
          <div className="flex items-center gap-6">
            <Link 
              href="/account/orders" 
              className={`flex items-center gap-2 text-sm font-semibold transition-colors duration-200 ${
                pathname === "/account/orders" || pathname.startsWith("/account/orders/")
                  ? "text-indigo-400"
                  : "text-slate-300 hover:text-white"
              }`}
            >
              <ClipboardList className="h-4.5 w-4.5" />
              <span className="hidden sm:inline">My Orders</span>
            </Link>

            <span className="h-4 w-px bg-white/10 hidden sm:inline" />

            {/* Profile widget */}
            {user && (
              <div className="flex items-center gap-3">
                <div className="h-8 w-8 rounded-full bg-indigo-500/10 border border-indigo-400/20 flex items-center justify-center hidden sm:flex">
                  <User className="h-4 w-4 text-indigo-300" />
                </div>
                <div className="flex flex-col text-left hidden md:flex">
                  <span className="text-xs font-bold text-slate-200 leading-none">{user.name}</span>
                  <span className="text-[10px] text-slate-400 leading-tight">Customer</span>
                </div>
                <button
                  onClick={logout}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold bg-white/5 border border-white/5 text-slate-300 hover:text-red-400 hover:bg-red-500/5 transition-all duration-200"
                  title="Logout"
                >
                  <LogOut className="h-3.5 w-3.5" />
                  <span className="hidden sm:inline">Sign Out</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 md:px-8 py-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="border-t border-white/5 py-6 text-center text-xs text-slate-500 bg-[#06090f]/50">
        <div className="max-w-7xl mx-auto px-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p>© 2026 Aura Design Storefront Customer Module. All rights reserved.</p>
          <div className="flex items-center gap-4 text-slate-400">
            <span className="flex items-center gap-1">Next.js Framework</span>
            <span className="h-3 w-px bg-white/10" />
            <span className="flex items-center gap-1">Framer Motion</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

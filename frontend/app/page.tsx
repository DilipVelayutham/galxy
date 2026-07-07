"use client";

import Link from "next/link";
import { useAuth } from "../context/AuthContext";
import { LogOut, User, Key, Shield, LogIn } from "lucide-react";

export default function Home() {
  const { user, logout, loading } = useAuth();

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-[#0B0B0F] px-6 text-[#F4F4F7]">
      <main className="w-full max-w-2xl text-center">
        {/* Glow neon title */}
        <h1 className="text-5xl font-extrabold tracking-widest text-[#F4F4F7] uppercase mb-4">
          GAL<span className="text-[#FF2E8A] drop-shadow-[0_0_12px_#FF2E8A]">XY</span>
        </h1>
        <p className="text-lg text-[#8A8A97] mb-12 uppercase tracking-widest">
          Custom Lighting & Craft Studio
        </p>

        {/* User Session Info */}
        <div className="mb-12 p-6 rounded-xl border border-white/5 bg-[#16161C]/50 backdrop-blur-md">
          {loading ? (
            <p className="text-sm text-[#18E7FF] animate-pulse">Hydrating session...</p>
          ) : user ? (
            <div>
              <p className="text-sm text-[#8A8A97] uppercase tracking-wider mb-2">Logged in as</p>
              <h3 className="text-xl font-bold text-[#18E7FF]">{user.name}</h3>
              <p className="text-sm text-[#8A8A97]">{user.email}</p>
              <button
                onClick={logout}
                className="mt-4 px-4 py-2 rounded-lg text-xs font-semibold uppercase tracking-wider text-black bg-[#FF2E8A] hover:bg-[#FF2E8A]/90 transition-colors inline-flex items-center gap-1.5 shadow-[0_0_10px_rgba(255,46,138,0.3)]"
              >
                <LogOut size={14} /> Log Out
              </button>
            </div>
          ) : (
            <div>
              <p className="text-sm text-[#8A8A97] uppercase tracking-wider">No active session found</p>
              <div className="mt-4 flex justify-center gap-4">
                <Link
                  href="/login"
                  className="px-5 py-2.5 rounded-lg text-sm font-semibold uppercase tracking-wider text-black bg-[#18E7FF] hover:bg-[#18E7FF]/90 transition-all duration-200 inline-flex items-center gap-1.5 shadow-[0_0_15px_rgba(24,231,255,0.4)]"
                >
                  <LogIn size={16} /> Log In
                </Link>
                <Link
                  href="/signup"
                  className="px-5 py-2.5 rounded-lg text-sm font-semibold uppercase tracking-wider border border-white/10 hover:border-white/20 transition-all duration-200"
                >
                  Sign Up
                </Link>
              </div>
            </div>
          )}
        </div>

        {/* Navigation Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Link
            href="/account/profile"
            className="p-5 rounded-xl border border-white/5 bg-[#16161C]/30 hover:bg-[#16161C]/50 hover:border-[#18E7FF]/50 transition-all duration-300 group text-left"
          >
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-[#18E7FF]/10 text-[#18E7FF] group-hover:shadow-[0_0_10px_rgba(24,231,255,0.2)]">
                <User size={20} />
              </div>
              <div>
                <h4 className="font-bold text-[#F4F4F7]">Customer Profile</h4>
                <p className="text-xs text-[#8A8A97]">Requires AuthGuard wrapper</p>
              </div>
            </div>
          </Link>

          <Link
            href="/forgot-password"
            className="p-5 rounded-xl border border-white/5 bg-[#16161C]/30 hover:bg-[#16161C]/50 hover:border-[#FF2E8A]/50 transition-all duration-300 group text-left"
          >
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-[#FF2E8A]/10 text-[#FF2E8A] group-hover:shadow-[0_0_10px_rgba(255,46,138,0.2)]">
                <Key size={20} />
              </div>
              <div>
                <h4 className="font-bold text-[#F4F4F7]">Password Recovery</h4>
                <p className="text-xs text-[#8A8A97]">In3 recovery simulation</p>
              </div>
            </div>
          </Link>

          <Link
            href="/admin/login"
            className="p-5 rounded-xl border border-white/5 bg-[#16161C]/30 hover:bg-[#16161C]/50 hover:border-[#FF2E8A]/50 transition-all duration-300 group text-left md:col-span-2"
          >
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-[#FF2E8A]/10 text-[#FF2E8A] group-hover:shadow-[0_0_10px_rgba(255,46,138,0.2)]">
                <Shield size={20} />
              </div>
              <div>
                <h4 className="font-bold text-[#F4F4F7]">Admin CMS Portal</h4>
                <p className="text-xs text-[#8A8A97]">Fully isolated admin login</p>
              </div>
            </div>
          </Link>
        </div>
      </main>
    </div>
  );
}

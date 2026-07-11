"use client";

import React, { useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { useToast } from "@/context/ToastContext";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { LogIn, Loader2, ArrowLeft } from "lucide-react";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const { login } = useAuth();
  const { showToast } = useToast();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      showToast("Email and password are required", "warning");
      return;
    }

    setSubmitting(true);
    try {
      const res = await login(email, password);
      if (res.success) {
        showToast("Logged in successfully!", "success");
        
        // Silent check on redirect role
        const session = await fetch("/api/auth/refresh", { method: "POST" });
        if (session.ok) {
          const body = await session.json();
          if (body.data?.user?.role === "super_admin") {
            router.push("/admin/dashboard");
            return;
          }
        }
        router.push("/");
      } else {
        showToast(res.message || "Invalid credentials", "error");
      }
    } catch {
      showToast("Login request failed", "error");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-void-black text-text-primary flex flex-col justify-center py-12 sm:px-6 lg:px-8 relative selection:bg-neon-pink selection:text-void-black">
      {/* Background Soft Glows */}
      <div className="absolute top-1/4 left-1/4 w-80 h-80 rounded-full bg-neon-blue/5 blur-[100px] pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-80 h-80 rounded-full bg-neon-pink/5 blur-[100px] pointer-events-none" />

      <div className="max-w-md w-full mx-auto px-6 relative z-10">
        <Link href="/" className="inline-flex items-center gap-1 text-xs text-text-muted hover:text-neon-blue font-bold tracking-wider mb-8">
          <ArrowLeft className="w-3.5 h-3.5" /> Back to Store
        </Link>

        <div className="p-8 rounded-2xl glass-panel border border-panel-charcoal flex flex-col gap-6">
          <div className="text-center">
            <h2 className="text-2xl font-black tracking-tight text-text-primary uppercase">
              Account <span className="text-neon-blue text-glow-blue animate-pulse">Login</span>
            </h2>
            <p className="text-xs text-text-muted mt-2">
              Sign in to manage custom configurations, wishlists, and track live order progress.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <div className="flex flex-col gap-1.5">
              <label className="text-[10px] text-text-muted uppercase font-bold tracking-wider">Email Address</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="w-full p-3 rounded-lg bg-void-black border border-panel-charcoal focus:border-neon-blue/40 text-sm text-text-primary focus:outline-none focus:glow-blue transition-all"
                required
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <label className="text-[10px] text-text-muted uppercase font-bold tracking-wider">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full p-3 rounded-lg bg-void-black border border-panel-charcoal focus:border-neon-blue/40 text-sm text-text-primary focus:outline-none focus:glow-blue transition-all"
                required
              />
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="mt-2 w-full p-3.5 rounded-lg bg-panel-charcoal hover:bg-void-black border border-neon-blue/40 text-neon-blue font-bold text-sm tracking-wider glow-blue-hover transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
            >
              {submitting ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <>
                  <LogIn className="w-4 h-4" /> SIGN IN
                </>
              )}
            </button>
          </form>

          <div className="text-center text-xs text-text-muted border-t border-panel-charcoal/50 pt-4">
            Don't have an account?{" "}
            <Link href="/signup" className="text-neon-pink hover:underline font-bold">
              Sign Up
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

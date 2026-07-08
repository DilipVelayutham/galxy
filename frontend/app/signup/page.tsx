"use client";

import React, { useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { useToast } from "@/context/ToastContext";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { UserPlus, Loader2, ArrowLeft } from "lucide-react";

export default function SignupPage() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const { signup } = useAuth();
  const { showToast } = useToast();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !email || !phone || !password) {
      showToast("All fields are required", "warning");
      return;
    }

    setSubmitting(true);
    try {
      const res = await signup(name, email, phone, password);
      if (res.success) {
        showToast("Registration successful! Please login.", "success");
        router.push("/login");
      } else {
        showToast(res.message || "Failed to register account", "error");
      }
    } catch {
      showToast("Signup request failed", "error");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-void-black text-text-primary flex flex-col justify-center py-12 sm:px-6 lg:px-8 relative selection:bg-neon-pink selection:text-void-black">
      <div className="absolute top-1/4 left-1/4 w-80 h-80 rounded-full bg-neon-blue/5 blur-[100px] pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-80 h-80 rounded-full bg-neon-pink/5 blur-[100px] pointer-events-none" />

      <div className="max-w-md w-full mx-auto px-6 relative z-10">
        <Link href="/login" className="inline-flex items-center gap-1 text-xs text-text-muted hover:text-neon-pink font-bold tracking-wider mb-8">
          <ArrowLeft className="w-3.5 h-3.5" /> Back to Login
        </Link>

        <div className="p-8 rounded-2xl glass-panel border border-panel-charcoal flex flex-col gap-6">
          <div className="text-center">
            <h2 className="text-2xl font-black tracking-tight text-text-primary uppercase">
              Create <span className="text-neon-pink text-glow-pink animate-pulse">Account</span>
            </h2>
            <p className="text-xs text-text-muted mt-2">
              Join GALXY to configure neon signs, lamps, and quilled art designs.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <div className="flex flex-col gap-1.5">
              <label className="text-[10px] text-text-muted uppercase font-bold tracking-wider">Full Name</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Rohan Sharma"
                className="w-full p-3 rounded-lg bg-void-black border border-panel-charcoal focus:border-neon-pink/40 text-sm text-text-primary focus:outline-none focus:glow-pink transition-all"
                required
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <label className="text-[10px] text-text-muted uppercase font-bold tracking-wider">Email Address</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="w-full p-3 rounded-lg bg-void-black border border-panel-charcoal focus:border-neon-pink/40 text-sm text-text-primary focus:outline-none focus:glow-pink transition-all"
                required
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <label className="text-[10px] text-text-muted uppercase font-bold tracking-wider">Phone Number</label>
              <input
                type="text"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="+91 99999 99999"
                className="w-full p-3 rounded-lg bg-void-black border border-panel-charcoal focus:border-neon-pink/40 text-sm text-text-primary focus:outline-none focus:glow-pink transition-all"
                required
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <label className="text-[10px] text-text-muted uppercase font-bold tracking-wider">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Minimum 6 characters"
                className="w-full p-3 rounded-lg bg-void-black border border-panel-charcoal focus:border-neon-pink/40 text-sm text-text-primary focus:outline-none focus:glow-pink transition-all"
                required
              />
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="mt-2 w-full p-3.5 rounded-lg bg-panel-charcoal hover:bg-void-black border border-neon-pink/40 text-neon-pink font-bold text-sm tracking-wider glow-pink-hover transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
            >
              {submitting ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <>
                  <UserPlus className="w-4 h-4" /> REGISTER
                </>
              )}
            </button>
          </form>

          <div className="text-center text-xs text-text-muted border-t border-panel-charcoal/50 pt-4">
            Already have an account?{" "}
            <Link href="/login" className="text-neon-blue hover:underline font-bold">
              Sign In
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

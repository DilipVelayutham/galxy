"use client";

import Link from "next/link";
import { useState } from "react";
import { validateEmail } from "../../../lib/validators";
import { Loader2 } from "lucide-react";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setMessage("");

    const emailVal = validateEmail(email);
    if (!emailVal.isValid) {
      setError(emailVal.error || "Invalid email");
      return;
    }

    setIsSubmitting(true);
    try {
      // In3 (Tharani) will connect this to POST /api/auth/forgot-password.
      // According to specifications, it must show the identical success message 
      // regardless of whether the email is registered or not (anti-enumeration).
      setMessage("If this email is registered, a password reset link has been sent.");
    } catch (err) {
      setError("An error occurred. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-screen flex-col items-center justify-center px-4 bg-[#0B0B0F]">
      <Link 
        href="/" 
        className="mb-8 text-2xl font-bold tracking-widest text-[#F4F4F7] hover:text-[#18E7FF] transition-colors"
      >
        GAL<span className="text-[#FF2E8A]">XY</span>
      </Link>

      <div className="w-full max-w-md p-8 rounded-2xl border border-white/10 bg-[#16161C]/75 backdrop-blur-xl shadow-[0_0_50px_rgba(24,231,255,0.05)]">
        <h2 className="text-2xl font-bold text-center text-[#F4F4F7]">
          FORGOT <span className="text-[#FF2E8A]">PASSWORD</span>
        </h2>
        <p className="mt-2 text-sm text-center text-[#8A8A97]">
          Enter your email address to receive a recovery link.
        </p>

        {message && (
          <div className="mt-4 p-3 rounded-lg bg-green-500/10 border border-green-500/20 text-green-400 text-sm text-center">
            {message}
          </div>
        )}

        {error && (
          <div className="mt-4 p-3 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-400 text-sm text-center">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-[#8A8A97] mb-1">
              Email Address
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              className="w-full px-4 py-3 rounded-lg border bg-[#0B0B0F]/50 text-[#F4F4F7] outline-none transition-all duration-200 border-white/10 focus:border-[#18E7FF] focus:shadow-[0_0_10px_rgba(24,231,255,0.2)]"
            />
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full py-3 rounded-lg font-semibold tracking-wider text-black bg-[#18E7FF] hover:bg-[#18E7FF]/90 transition-all duration-200 flex items-center justify-center gap-2 shadow-[0_0_15px_rgba(24,231,255,0.4)] active:scale-95 disabled:opacity-50"
          >
            {isSubmitting ? <Loader2 className="h-5 w-5 animate-spin" /> : "SEND LINK"}
          </button>
        </form>

        <div className="mt-6 text-sm text-center text-[#8A8A97]">
          Back to{" "}
          <Link href="/login" className="font-medium text-[#FF2E8A] hover:underline">
            Log In
          </Link>
        </div>
      </div>
    </div>
  );
}

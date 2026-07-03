"use client";

import Link from "next/link";
import { useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { validatePassword } from "../../../lib/validators";
import { Eye, EyeOff, Loader2 } from "lucide-react";

function ResetPasswordContent() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token") || "";

  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setMessage("");

    if (!token) {
      setError("Reset token is missing or invalid.");
      return;
    }

    const passVal = validatePassword(password);
    if (!passVal.isValid) {
      setError(passVal.error || "Weak password");
      return;
    }

    setIsSubmitting(true);
    try {
      // In3 (Tharani) will connect this to POST /api/auth/reset-password.
      setMessage("Password has been reset successfully.");
    } catch (err) {
      setError("Failed to reset password. Token may have expired.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="w-full max-w-md p-8 rounded-2xl border border-white/10 bg-[#16161C]/75 backdrop-blur-xl shadow-[0_0_50px_rgba(24,231,255,0.05)]">
      <h2 className="text-2xl font-bold text-center text-[#F4F4F7]">
        RESET <span className="text-[#FF2E8A]">PASSWORD</span>
      </h2>
      <p className="mt-2 text-sm text-center text-[#8A8A97]">
        Enter your new secure password below.
      </p>

      {message && (
        <div className="mt-4 p-3 rounded-lg bg-green-500/10 border border-green-500/20 text-green-400 text-sm text-center">
          {message}
          <div className="mt-2">
            <Link href="/login" className="font-semibold underline text-[#18E7FF]">
              Click here to log in
            </Link>
          </div>
        </div>
      )}

      {error && (
        <div className="mt-4 p-3 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-400 text-sm text-center">
          {error}
        </div>
      )}

      {!message && (
        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-[#8A8A97] mb-1">
              New Password
            </label>
            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full pl-4 pr-10 py-3 rounded-lg border bg-[#0B0B0F]/50 text-[#F4F4F7] outline-none transition-all duration-200 border-white/10 focus:border-[#18E7FF] focus:shadow-[0_0_10px_rgba(24,231,255,0.2)]"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-[#8A8A97] hover:text-[#F4F4F7]"
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full py-3 rounded-lg font-semibold tracking-wider text-black bg-[#18E7FF] hover:bg-[#18E7FF]/90 transition-all duration-200 flex items-center justify-center gap-2 shadow-[0_0_15px_rgba(24,231,255,0.4)] active:scale-95 disabled:opacity-50"
          >
            {isSubmitting ? <Loader2 className="h-5 w-5 animate-spin" /> : "RESET PASSWORD"}
          </button>
        </form>
      )}
    </div>
  );
}

export default function ResetPasswordPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center px-4 bg-[#0B0B0F]">
      <Link 
        href="/" 
        className="mb-8 text-2xl font-bold tracking-widest text-[#F4F4F7] hover:text-[#18E7FF] transition-colors"
      >
        GAL<span className="text-[#FF2E8A]">XY</span>
      </Link>
      
      <Suspense fallback={
        <div className="h-64 w-full max-w-md rounded-2xl bg-[#16161C]/50 border border-white/5 animate-pulse" />
      }>
        <ResetPasswordContent />
      </Suspense>
    </div>
  );
}

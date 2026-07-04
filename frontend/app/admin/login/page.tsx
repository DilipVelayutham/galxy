"use client";

import React, { useState } from "react";
import { useAdminAuth } from "../../../context/AdminAuthContext";
import { Eye, EyeOff, Loader2 } from "lucide-react";
import Link from "next/link";

export default function AdminLoginPage() {
  const { login } = useAdminAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState<{ auth?: string; email?: string; password?: string }>({});

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});

    // Simple validation
    const newErrors: typeof errors = {};
    if (!email.trim()) newErrors.email = "Email is required";
    if (!password) newErrors.password = "Password is required";
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setIsSubmitting(true);
    try {
      await login(email, password);
      // Redirect to admin dashboard
      window.location.href = "/admin/dashboard";
    } catch (err: any) {
      setErrors({ auth: err.message || "Invalid admin credentials" });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#0B0B0F] px-4 text-[#F4F4F7]">
      <div className="w-full max-w-sm p-6 rounded-lg border border-white/5 bg-[#16161C] shadow-lg">
        <h2 className="text-xl font-bold uppercase tracking-wider text-center text-[#F4F4F7]">
          GALXY <span className="text-[#FF2E8A]">CMS</span>
        </h2>
        <p className="mt-1 text-xs text-center text-[#8A8A97] uppercase tracking-wide">
          Administrator Login
        </p>

        {errors.auth && (
          <div className="mt-4 p-2 rounded bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs text-center">
            {errors.auth}
          </div>
        )}

        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          <div>
            <label className="block text-xxs font-bold uppercase tracking-widest text-[#8A8A97] mb-1">
              Email Address
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="admin@galxy.in"
              className="w-full px-3 py-2 text-sm rounded border bg-[#0B0B0F] text-[#F4F4F7] outline-none border-white/10 focus:border-[#FF2E8A]"
            />
            {errors.email && <p className="mt-1 text-xs text-amber-400">{errors.email}</p>}
          </div>

          <div>
            <label className="block text-xxs font-bold uppercase tracking-widest text-[#8A8A97] mb-1">
              Password
            </label>
            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full pl-3 pr-9 py-2 text-sm rounded border bg-[#0B0B0F] text-[#F4F4F7] outline-none border-white/10 focus:border-[#FF2E8A]"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-2.5 top-1/2 -translate-y-1/2 text-[#8A8A97] hover:text-[#F4F4F7]"
              >
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
            {errors.password && <p className="mt-1 text-xs text-amber-400">{errors.password}</p>}
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full py-2.5 rounded font-semibold text-sm tracking-wider text-black bg-[#FF2E8A] hover:bg-[#FF2E8A]/90 transition-colors flex items-center justify-center gap-2 active:scale-98 disabled:opacity-50"
          >
            {isSubmitting ? <Loader2 className="h-4 w-4 animate-spin" /> : "ENTER PANEL"}
          </button>
        </form>
        
        <div className="mt-6 text-center">
          <Link href="/" className="text-xxs text-[#8A8A97] hover:text-[#F4F4F7] tracking-wider uppercase underline">
            Back to Shop
          </Link>
        </div>
      </div>
    </div>
  );
}

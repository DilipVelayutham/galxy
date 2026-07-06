"use client";

import React, { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "../../context/AuthContext";
import { validateEmail, validatePassword, validatePhone } from "../../lib/validators";
import { Eye, EyeOff, Loader2 } from "lucide-react";

interface AuthFormProps {
  initialMode?: "login" | "signup";
}

export const AuthForm: React.FC<AuthFormProps> = ({ initialMode = "login" }) => {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { login, signup } = useAuth();
  
  const [isLogin, setIsLogin] = useState<boolean>(initialMode === "login");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  
  // Inline validation error states
  const [errors, setErrors] = useState<{
    name?: string;
    email?: string;
    phone?: string;
    password?: string;
    auth?: string;
  }>({});
  
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const redirectPath = searchParams.get("redirect") || "/";

  // Handles client-side validations
  const validateForm = (): boolean => {
    const newErrors: typeof errors = {};
    let isValid = true;

    if (!isLogin) {
      if (!name.trim()) {
        newErrors.name = "Name is required";
        isValid = false;
      }
      
      const phoneVal = validatePhone(phone);
      if (!phoneVal.isValid) {
        newErrors.phone = phoneVal.error;
        isValid = false;
      }
    }

    const emailVal = validateEmail(email);
    if (!emailVal.isValid) {
      newErrors.email = emailVal.error;
      isValid = false;
    }

    const passVal = validatePassword(password);
    if (!passVal.isValid) {
      newErrors.password = passVal.error;
      isValid = false;
    }

    setErrors(newErrors);
    return isValid;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});
    
    if (!validateForm()) return;

    setIsSubmitting(true);
    try {
      if (isLogin) {
        await login(email, password);
      } else {
        await signup(name, email, phone, password);
      }
      router.push(redirectPath);
    } catch (err: any) {
      setErrors({ auth: err.message || "An authentication error occurred" });
    } finally {
      setIsSubmitting(false);
    }
  };

  const toggleMode = () => {
    setIsLogin(!isLogin);
    setErrors({});
    setName("");
    setEmail("");
    setPhone("");
    setPassword("");
  };

  return (
    <div className="w-full max-w-md p-8 rounded-2xl border border-white/10 bg-[#16161C]/75 backdrop-blur-xl shadow-[0_0_50px_rgba(24,231,255,0.05)] transition-all duration-300 hover:shadow-[0_0_50px_rgba(24,231,255,0.1)]">
      {/* Title */}
      <h2 className="text-3xl font-bold text-center tracking-wide text-[#F4F4F7]">
        {isLogin ? (
          <>
            WELCOME TO <span className="text-[#FF2E8A] drop-shadow-[0_0_8px_#FF2E8A]">GALXY</span>
          </>
        ) : (
          <>
            CREATE YOUR <span className="text-[#18E7FF] drop-shadow-[0_0_8px_#18E7FF]">ACCOUNT</span>
          </>
        )}
      </h2>
      <p className="mt-2 text-sm text-center text-[#8A8A97]">
        {isLogin ? "Log in to configure and track orders" : "Sign up to start configuring custom products"}
      </p>

      {/* Global Auth Error */}
      {errors.auth && (
        <div className="mt-4 p-3 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-400 text-sm text-center">
          {errors.auth}
        </div>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit} className="mt-6 space-y-4">
        {/* Name (Signup only) */}
        {!isLogin && (
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-[#8A8A97] mb-1">
              Full Name
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Dilip Velayutham"
              className="w-full px-4 py-3 rounded-lg border bg-[#0B0B0F]/50 text-[#F4F4F7] outline-none transition-all duration-200 border-white/10 focus:border-[#18E7FF] focus:shadow-[0_0_10px_rgba(24,231,255,0.2)]"
            />
            {errors.name && <p className="mt-1 text-xs text-amber-400">{errors.name}</p>}
          </div>
        )}

        {/* Email */}
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
          {errors.email && <p className="mt-1 text-xs text-amber-400">{errors.email}</p>}
        </div>

        {/* Phone (Signup only) */}
        {!isLogin && (
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-[#8A8A97] mb-1">
              Mobile Number
            </label>
            <input
              type="text"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="9876543210"
              className="w-full px-4 py-3 rounded-lg border bg-[#0B0B0F]/50 text-[#F4F4F7] outline-none transition-all duration-200 border-white/10 focus:border-[#18E7FF] focus:shadow-[0_0_10px_rgba(24,231,255,0.2)]"
            />
            {errors.phone && <p className="mt-1 text-xs text-amber-400">{errors.phone}</p>}
          </div>
        )}

        {/* Password */}
        <div>
          <label className="block text-xs font-semibold uppercase tracking-wider text-[#8A8A97] mb-1">
            Password
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
              className="absolute right-3 top-1/2 -translate-y-1/2 text-[#8A8A97] hover:text-[#F4F4F7] transition-colors"
            >
              {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          </div>
          {errors.password && <p className="mt-1 text-xs text-amber-400">{errors.password}</p>}
        </div>

        {/* CTA Button */}
        <button
          type="submit"
          disabled={isSubmitting}
          className={`w-full py-3 mt-2 rounded-lg font-semibold tracking-wider text-black bg-[#18E7FF] hover:bg-[#18E7FF]/90 transition-all duration-200 flex items-center justify-center gap-2 shadow-[0_0_15px_rgba(24,231,255,0.4)] hover:shadow-[0_0_25px_rgba(24,231,255,0.6)] active:scale-95 disabled:opacity-50 disabled:pointer-events-none`}
        >
          {isSubmitting ? (
            <Loader2 className="h-5 w-5 animate-spin" />
          ) : isLogin ? (
            "LOG IN"
          ) : (
            "SIGN UP"
          )}
        </button>
      </form>

      {/* Switch Link */}
      <div className="mt-6 text-sm text-center text-[#8A8A97]">
        {isLogin ? "Don't have an account?" : "Already have an account?"}{" "}
        <button
          onClick={toggleMode}
          className="font-medium text-[#FF2E8A] hover:underline transition-colors"
        >
          {isLogin ? "Sign Up" : "Log In"}
        </button>
      </div>
    </div>
  );
};

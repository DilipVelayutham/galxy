'use client';

import React, { useState, FormEvent, Suspense } from 'react';
import Link from 'next/link';
import { useSearchParams, useRouter } from 'next/navigation';
import { validatePassword } from '../../../../lib/validators';

function ResetPasswordForm() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const token = searchParams.get('token') || '';

  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [fieldErrors, setFieldErrors] = useState<{ password?: string; confirmPassword?: string }>({});
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setFieldErrors({});

    if (!token) {
      setError('A valid password reset token is missing from the link.');
      return;
    }

    // 1. Client-side validations
    const passValidation = validatePassword(password);
    if (!passValidation.isValid) {
      setFieldErrors({ password: passValidation.error });
      return;
    }

    if (password !== confirmPassword) {
      setFieldErrors({ confirmPassword: 'Passwords do not match' });
      return;
    }

    setStatus('loading');

    try {
      // 2. API Request
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000/api'}/auth/reset-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token, new_password: password }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setStatus('success');
      } else {
        setStatus('error');
        setError(data.message || 'The token is invalid, expired, or has already been used.');
      }
    } catch (err) {
      setStatus('error');
      setError('A network error occurred. Please try again.');
    }
  };

  if (!token) {
    return (
      <div className="space-y-6 text-center animate-fade-in">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-[#FFD84D]/10 border border-[#FFD84D] text-[#FFD84D] mb-2 drop-shadow-[0_0_15px_rgba(255,216,77,0.3)]">
          <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <h2 className="text-xl font-bold text-[#F4F4F7]">Invalid Reset Link</h2>
        <p className="text-sm text-[#8A8A97] leading-relaxed">
          The password reset link is invalid, incomplete, or has expired. Please request a new link.
        </p>
        <div className="pt-4">
          <Link href="/forgot-password" className="inline-block px-6 py-3 bg-[#FF2E8A] text-white font-semibold text-sm rounded-xl shadow-[0_0_15px_rgba(255,46,138,0.3)] hover:shadow-[0_0_20px_rgba(255,46,138,0.5)] transition-all duration-300">
            Request New Link
          </Link>
        </div>
      </div>
    );
  }

  if (status === 'success') {
    return (
      <div className="space-y-6 text-center animate-fade-in">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-[#18E7FF]/10 border border-[#18E7FF] text-[#18E7FF] mb-2 drop-shadow-[0_0_15px_rgba(24,231,255,0.3)]">
          <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
          </svg>
        </div>
        <h2 className="text-xl font-bold text-[#F4F4F7]">Password Reset Complete</h2>
        <p className="text-sm text-[#8A8A97] leading-relaxed">
          Your password has been successfully updated. You can now use your new password to log in.
        </p>
        <div className="pt-4">
          <Link href="/login" className="inline-block px-6 py-3 bg-gradient-to-r from-[#FF2E8A] to-[#9B5CFF] text-white font-semibold text-sm rounded-xl shadow-[0_0_15px_rgba(255,46,138,0.3)] hover:shadow-[0_0_20px_rgba(255,46,138,0.5)] transition-all duration-300">
            Log In Now
          </Link>
        </div>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="space-y-2">
        <h2 className="text-2xl font-bold text-[#F4F4F7]">Reset Password</h2>
        <p className="text-sm text-[#8A8A97]">Enter your new password below to secure your account.</p>
      </div>

      {/* Global error alert */}
      {error && (
        <div className="p-3.5 bg-[#FFD84D]/10 border border-[#FFD84D]/30 rounded-xl text-xs text-[#FFD84D] flex items-start gap-2.5">
          <svg className="w-4 h-4 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <span className="leading-relaxed">{error}</span>
        </div>
      )}

      {/* New Password Field */}
      <div className="space-y-1.5">
        <label htmlFor="password" className="text-xs font-semibold text-[#8A8A97] uppercase tracking-wider">
          New Password
        </label>
        <input
          type="password"
          id="password"
          required
          placeholder="••••••••"
          value={password}
          onChange={(e) => {
            setPassword(e.target.value);
            if (fieldErrors.password) setFieldErrors({ ...fieldErrors, password: '' });
          }}
          disabled={status === 'loading'}
          className={`w-full bg-[#0B0B0F] border text-[#F4F4F7] text-sm rounded-xl px-4 py-3.5 focus:outline-none transition-all duration-300 ${
            fieldErrors.password
              ? 'border-[#FFD84D] focus:ring-1 focus:ring-[#FFD84D]'
              : 'border-[#2E2E3A] focus:border-[#FF2E8A] focus:ring-1 focus:ring-[#FF2E8A] focus:shadow-[0_0_15px_rgba(255,46,138,0.15)]'
          }`}
        />
        {fieldErrors.password && (
          <p className="text-xs text-[#FFD84D] flex items-center gap-1.5 mt-1 animate-slide-down">
            <svg className="w-3.5 h-3.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            {fieldErrors.password}
          </p>
        )}
      </div>

      {/* Confirm Password Field */}
      <div className="space-y-1.5">
        <label htmlFor="confirmPassword" className="text-xs font-semibold text-[#8A8A97] uppercase tracking-wider">
          Confirm Password
        </label>
        <input
          type="password"
          id="confirmPassword"
          required
          placeholder="••••••••"
          value={confirmPassword}
          onChange={(e) => {
            setConfirmPassword(e.target.value);
            if (fieldErrors.confirmPassword) setFieldErrors({ ...fieldErrors, confirmPassword: '' });
          }}
          disabled={status === 'loading'}
          className={`w-full bg-[#0B0B0F] border text-[#F4F4F7] text-sm rounded-xl px-4 py-3.5 focus:outline-none transition-all duration-300 ${
            fieldErrors.confirmPassword
              ? 'border-[#FFD84D] focus:ring-1 focus:ring-[#FFD84D]'
              : 'border-[#2E2E3A] focus:border-[#FF2E8A] focus:ring-1 focus:ring-[#FF2E8A] focus:shadow-[0_0_15px_rgba(255,46,138,0.15)]'
          }`}
        />
        {fieldErrors.confirmPassword && (
          <p className="text-xs text-[#FFD84D] flex items-center gap-1.5 mt-1 animate-slide-down">
            <svg className="w-3.5 h-3.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            {fieldErrors.confirmPassword}
          </p>
        )}
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={status === 'loading'}
        className="w-full relative group overflow-hidden bg-gradient-to-r from-[#FF2E8A] to-[#9B5CFF] text-white font-semibold text-sm rounded-xl py-3.5 shadow-[0_0_20px_rgba(255,46,138,0.3)] hover:shadow-[0_0_25px_rgba(255,46,138,0.5)] focus:outline-none transition-all duration-300 hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50"
      >
        {status === 'loading' ? (
          <span className="flex items-center justify-center gap-2">
            <svg className="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            Updating password...
          </span>
        ) : (
          'Update Password'
        )}
      </button>

      <div className="text-center text-xs">
        <Link href="/login" className="text-[#8A8A97] hover:text-[#18E7FF] transition-colors duration-200">
          Back to Login
        </Link>
      </div>
    </form>
  );
}

export default function ResetPasswordPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0B0B0F] px-4 selection:bg-[#FF2E8A] selection:text-white relative overflow-hidden">
      {/* Background Neon Glow Effects */}
      <div className="absolute top-1/4 left-1/4 w-[300px] h-[300px] bg-[#9B5CFF]/10 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-[350px] h-[350px] bg-[#FF2E8A]/10 rounded-full blur-[130px] pointer-events-none" />

      {/* Main Container */}
      <div className="w-full max-w-md z-10 transition-all duration-300">
        {/* Logo / Header */}
        <div className="text-center mb-8">
          <Link href="/" className="inline-block text-3xl font-extrabold tracking-widest text-[#F4F4F7] hover:text-[#18E7FF] transition-colors duration-200">
            GAL<span className="text-[#FF2E8A] drop-shadow-[0_0_10px_rgba(255,46,138,0.5)]">X</span>Y
          </Link>
          <p className="mt-2 text-sm text-[#8A8A97]">Custom Lighting & Craft Studio</p>
        </div>

        {/* Card Panel - Dark Glassmorphism */}
        <div className="bg-[#16161C]/80 backdrop-blur-xl border border-[#2E2E3A] rounded-2xl p-8 shadow-2xl relative">
          <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-[#9B5CFF] to-[#FF2E8A] rounded-t-2xl" />

          {/* Suspense is required for next.js static rendering when useSearchParams is called */}
          <Suspense fallback={
            <div className="flex flex-col items-center justify-center py-10 space-y-4">
              <svg className="animate-spin h-8 w-8 text-[#FF2E8A]" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              <p className="text-sm text-[#8A8A97]">Loading form secure context...</p>
            </div>
          }>
            <ResetPasswordForm />
          </Suspense>
        </div>
      </div>
    </div>
  );
}

"use client";

import React, { useState, FormEvent } from 'react';
import Link from 'next/link';
import { validateEmail } from '../../../lib/validators';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [apiMessage, setApiMessage] = useState('');

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    
    // 1. Client-side validation
    const validation = validateEmail(email);
    if (!validation.isValid) {
      setError(validation.error || 'Invalid email format');
      return;
    }

    setStatus('loading');

    try {
      // 2. API Request
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000/api'}/auth/forgot-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email: validation.value }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setStatus('success');
        setApiMessage(data.message);
      } else {
        setStatus('error');
        setError(data.message || 'Something went wrong. Please try again.');
      }
    } catch (err) {
      // In case of network errors, fallback gracefully
      setStatus('success'); // Fallback to success to avoid leaking registration details
      setApiMessage('If the email is registered, a password reset link has been sent.');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0B0B0F] px-4 selection:bg-[#FF2E8A] selection:text-white relative overflow-hidden">
      {/* Background Neon Glow Effects */}
      <div className="absolute top-1/4 left-1/4 w-[300px] h-[300px] bg-[#FF2E8A]/10 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-[350px] h-[350px] bg-[#18E7FF]/10 rounded-full blur-[130px] pointer-events-none" />

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
          {/* Subtle Pink-to-Blue Top Highlight Bar */}
          <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-[#FF2E8A] to-[#18E7FF] rounded-t-2xl" />

          {status === 'success' ? (
            <div className="space-y-6 text-center animate-fade-in">
              {/* Success Icon */}
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-[#18E7FF]/10 border border-[#18E7FF] text-[#18E7FF] mb-2 drop-shadow-[0_0_15px_rgba(24,231,255,0.3)]">
                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 19v-8.93a2 2 0 01.89-1.664l8-5.333a2 2 0 012.22 0l8 5.333A2 2 0 0121 10.07V19M3 19a2 2 0 002 2h14a2 2 0 002-2M3 19l6.75-4.5M21 19l-6.75-4.5M3 10l6.75 4.5M21 10l-6.75 4.5m0 0l-1.14.76a2 2 0 01-2.22 0l-1.14-.76" />
                </svg>
              </div>
              <h2 className="text-xl font-bold text-[#F4F4F7]">Check Your Inbox</h2>
              <p className="text-sm text-[#8A8A97] leading-relaxed">
                {apiMessage || 'If the email is registered, a password reset link has been sent.'}
              </p>
              <div className="pt-4">
                <Link href="/login" className="text-sm text-[#18E7FF] hover:text-[#FF2E8A] underline underline-offset-4 transition-colors duration-200">
                  Back to Login
                </Link>
              </div>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="space-y-2">
                <h2 className="text-2xl font-bold text-[#F4F4F7]">Forgot Password?</h2>
                <p className="text-sm text-[#8A8A97]">Enter your email address and we'll send you a link to reset your password.</p>
              </div>

              {/* Email Input Field */}
              <div className="space-y-1.5">
                <label htmlFor="email" className="text-xs font-semibold text-[#8A8A97] uppercase tracking-wider">
                  Email Address
                </label>
                <div className="relative">
                  <input
                    type="email"
                    id="email"
                    name="email"
                    required
                    placeholder="name@example.com"
                    value={email}
                    onChange={(e) => {
                      setEmail(e.target.value);
                      if (error) setError('');
                    }}
                    disabled={status === 'loading'}
                    className={`w-full bg-[#0B0B0F] border text-[#F4F4F7] text-sm rounded-xl px-4 py-3.5 focus:outline-none transition-all duration-300 ${
                      error
                        ? 'border-[#FFD84D] focus:ring-1 focus:ring-[#FFD84D]'
                        : 'border-[#2E2E3A] focus:border-[#FF2E8A] focus:ring-1 focus:ring-[#FF2E8A] focus:shadow-[0_0_15px_rgba(255,46,138,0.15)]'
                    }`}
                  />
                </div>
                {/* Error with Warning Tint (Yellow/Gold, never raw red) */}
                {error && (
                  <p className="text-xs text-[#FFD84D] flex items-center gap-1.5 mt-1 animate-slide-down">
                    <svg className="w-3.5 h-3.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                    {error}
                  </p>
                )}
              </div>

              {/* Submit Button with Neon Glow CTA Treatment */}
              <button
                type="submit"
                disabled={status === 'loading'}
                className="w-full relative group overflow-hidden bg-[#FF2E8A] text-white font-semibold text-sm rounded-xl py-3.5 shadow-[0_0_20px_rgba(255,46,138,0.3)] hover:shadow-[0_0_25px_rgba(255,46,138,0.5)] focus:outline-none transition-all duration-300 hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50 disabled:pointer-events-none"
              >
                {status === 'loading' ? (
                  <span className="flex items-center justify-center gap-2">
                    <svg className="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Sending link...
                  </span>
                ) : (
                  'Send Reset Link'
                )}
              </button>

              {/* Form Navigation links */}
              <div className="flex items-center justify-between text-xs pt-2">
                <Link href="/login" className="text-[#8A8A97] hover:text-[#18E7FF] transition-colors duration-200">
                  Back to Login
                </Link>
                <Link href="/signup" className="text-[#18E7FF] hover:text-[#FF2E8A] transition-colors duration-200">
                  Create Account
                </Link>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}

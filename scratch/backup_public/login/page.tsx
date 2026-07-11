'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../../../context/AuthContext';
import { Sparkles, Mail, Lock, ShieldAlert } from 'lucide-react';
import Header from '../../../components/Header';

export default function LoginPage() {
  const router = useRouter();
  const { login, triggerToast } = useAuth();
  const [email, setEmail] = useState('jaiganesh@galxy.in');
  const [password, setPassword] = useState('password123');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      triggerToast('Please fill in all fields', 'error');
      return;
    }

    setIsLoading(true);
    try {
      const success = await login(email);
      if (success) {
        // Redirect to cart since there might be a pending selection being auto-added!
        router.push('/cart');
      }
    } catch (err) {
      console.error(err);
      triggerToast('Login failed', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-bg-void text-text-primary">
      <Header />

      <main className="flex-1 flex items-center justify-center p-6 max-w-md mx-auto w-full">
        <div className="w-full rounded-xl glass-panel border-white/5 p-8 shadow-glow-pink relative">
          <div className="flex flex-col items-center text-center mb-8">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-tr from-neon-pink to-neon-violet flex items-center justify-center shadow-glow-pink mb-3">
              <Sparkles size={20} className="text-[#0B0B0F]" />
            </div>
            <h2 className="text-2xl font-extrabold font-display text-text-primary">
              Sign In to Galxy
            </h2>
            <p className="text-text-muted text-xs mt-1 max-w-xs">
              Complete authentication to manage your cart, wishlist, and track orders in real-time.
            </p>
          </div>

          {/* Guest resume flow warning box */}
          {typeof window !== 'undefined' && sessionStorage.getItem('pending_cart_item') && (
            <div className="p-3.5 mb-6 rounded-lg bg-neon-blue/5 border border-neon-blue/20 flex gap-2 items-start text-xs text-text-primary">
              <ShieldAlert className="text-neon-blue flex-shrink-0 mt-0.5" size={14} />
              <div>
                <span className="font-bold text-neon-blue block uppercase tracking-wider text-[9px] mb-0.5">Resume selection pending</span>
                Signing in will automatically add your custom Neon Sign selection to your account cart.
              </div>
            </div>
          )}

          <form onSubmit={handleSubmit} className="flex flex-col gap-5">
            <div>
              <label className="text-[10px] font-bold text-text-muted uppercase tracking-widest block mb-2">
                Email Address
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-text-muted">
                  <Mail size={16} />
                </span>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 rounded-lg bg-surface-panel border border-white/10 text-sm text-text-primary focus:outline-none focus:border-neon-pink focus:ring-1 focus:ring-neon-pink transition-all"
                  required
                />
              </div>
            </div>

            <div>
              <label className="text-[10px] font-bold text-text-muted uppercase tracking-widest block mb-2">
                Password
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-text-muted">
                  <Lock size={16} />
                </span>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 rounded-lg bg-surface-panel border border-white/10 text-sm text-text-primary focus:outline-none focus:border-neon-pink focus:ring-1 focus:ring-neon-pink transition-all"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full mt-2 py-3 px-6 rounded-lg font-bold bg-gradient-to-r from-neon-pink to-neon-violet text-[#F4F4F7] shadow-glow-pink transition-all duration-300 transform hover:scale-[1.02] hover:brightness-110 disabled:opacity-50"
            >
              {isLoading ? 'Signing In...' : 'Sign In'}
            </button>
          </form>

          <div className="mt-6 text-center text-xs text-text-muted">
            Don&apos;t have an account? <span className="text-neon-pink cursor-pointer hover:underline">Sign Up</span>
          </div>
        </div>
      </main>
    </div>
  );
}

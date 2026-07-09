'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../../../context/AuthContext';
import Header from '../../../components/Header';
import { CheckCircle2, ShieldCheck, ArrowRight } from 'lucide-react';
import Link from 'next/link';

export default function CheckoutPage() {
  const router = useRouter();
  const { user, refreshCart, triggerToast } = useAuth();
  const [orderNumber, setOrderNumber] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) {
      router.push('/login');
      return;
    }

    // Process checkout: clear cart & generate order number
    const processCheckout = async () => {
      try {
        const res = await fetch('/api/cart/clear', { method: 'DELETE' });
        if (res.ok) {
          // Generate a mock order number
          const randNum = Math.floor(10000 + Math.random() * 90000);
          setOrderNumber(`GLX-2026-${randNum}`);
          await refreshCart();
          triggerToast('Order inquiry submitted successfully!', 'success');
        }
      } catch (err) {
        console.error(err);
        triggerToast('Error during checkout', 'error');
      } finally {
        setLoading(false);
      }
    };

    processCheckout();
  }, [user, refreshCart, router, triggerToast]);

  if (!user || loading) {
    return (
      <div className="min-h-screen flex flex-col bg-bg-void text-text-primary">
        <Header />
        <div className="flex-1 flex flex-col items-center justify-center py-20">
          <div className="w-8 h-8 rounded-full border-2 border-neon-blue border-t-transparent animate-spin mb-4" />
          <span className="text-sm text-text-muted font-semibold">Processing order inquiry...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-bg-void text-text-primary">
      <Header />

      <main className="flex-1 flex items-center justify-center p-6 max-w-lg mx-auto w-full">
        <div className="w-full rounded-xl glass-panel border-white/5 p-8 shadow-glow-blue text-center relative">
          {/* Success Icon */}
          <div className="w-16 h-16 rounded-full bg-neon-blue/10 border border-neon-blue flex items-center justify-center mx-auto mb-6 shadow-glow-blue animate-bounce">
            <CheckCircle2 size={32} className="text-neon-blue" />
          </div>

          <h2 className="text-3xl font-extrabold font-display text-text-primary text-glow-blue mb-2">
            Inquiry Submitted!
          </h2>
          <p className="text-text-muted text-sm max-w-sm mx-auto mb-8">
            Your custom product configuration details have been recorded. Asil will review the specifications and coordinate with you offline to finalize the quote.
          </p>

          {/* Details Card */}
          <div className="rounded-lg bg-surface-panel border border-white/10 p-5 mb-8 text-left">
            <div className="flex justify-between items-center mb-3">
              <span className="text-xs text-text-muted font-bold uppercase tracking-wider">Order Reference</span>
              <span className="text-xs font-mono font-bold text-neon-pink bg-neon-pink/10 px-2 py-0.5 rounded border border-neon-pink/20">
                {orderNumber}
              </span>
            </div>
            <div className="flex justify-between items-center mb-3">
              <span className="text-xs text-text-muted font-bold uppercase tracking-wider">Account</span>
              <span className="text-xs font-bold text-text-primary">{user.email}</span>
            </div>
            <div className="flex justify-between items-center border-t border-white/5 pt-3">
              <span className="text-xs text-text-muted font-bold uppercase tracking-wider">Status</span>
              <span className="text-xs font-bold text-neon-violet flex items-center gap-1">
                <ShieldCheck size={12} /> Received & Awaiting Review
              </span>
            </div>
          </div>

          {/* Action buttons */}
          <div className="flex flex-col gap-4">
            <Link
              href="/products/custom-neon-sign"
              className="w-full py-3 px-6 rounded-lg font-bold bg-neon-blue text-[#0B0B0F] shadow-glow-blue hover:brightness-110 transition-all duration-300 flex items-center justify-center gap-2"
            >
              Configure Another Product <ArrowRight size={16} />
            </Link>
            <Link
              href="/"
              className="w-full py-3 px-6 rounded-lg font-bold bg-surface-panel border border-white/10 text-text-primary hover:border-white/20 transition-all duration-300"
            >
              Return to Storefront
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}

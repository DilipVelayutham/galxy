import React from 'react';
import Link from 'next/link';
import Header from '../components/Header';
import { Sparkles, ShoppingBag, Sliders, CheckCircle2 } from 'lucide-react';

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col bg-bg-void text-text-primary">
      <Header />
      
      {/* Hero Section */}
      <main className="flex-1 flex flex-col justify-center items-center py-20 px-6 max-w-4xl mx-auto text-center relative overflow-hidden">
        {/* Decorative background glows */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-72 h-72 rounded-full bg-neon-pink/5 blur-3xl pointer-events-none" />
        <div className="absolute bottom-1/4 left-1/3 -translate-x-1/2 -translate-y-1/2 w-80 h-80 rounded-full bg-neon-blue/5 blur-3xl pointer-events-none" />
        
        {/* Title */}
        <div className="relative mb-6">
          <span className="text-xs font-bold tracking-widest text-neon-blue uppercase px-3 py-1 rounded-full border border-neon-blue/20 bg-neon-blue/5 inline-block mb-4 shadow-glow-blue animate-pulse">
            Custom LED & Craft Studio
          </span>
          <h1 className="text-5xl md:text-7xl font-extrabold font-display leading-tight tracking-tight text-glow-pink text-neon-pink animate-flicker">
            LIGHT UP YOUR SPACE
          </h1>
          <h2 className="text-3xl md:text-5xl font-extrabold font-display text-text-primary mt-2">
            Configure Your Custom Art
          </h2>
        </div>
        
        {/* Description */}
        <p className="text-text-muted text-base md:text-lg max-w-xl mb-10 leading-relaxed font-medium">
          Create bespoke neon signage, quilling designs, and moonlight lamps. Customise options in real-time, generate instant AI visual previews, and submit order inquiries.
        </p>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 mb-16 relative z-10">
          <Link
            href="/products/custom-neon-sign"
            className="py-3 px-8 rounded-lg font-bold bg-gradient-to-r from-neon-pink to-neon-violet text-[#F4F4F7] shadow-glow-pink transition-all duration-300 transform hover:scale-[1.03] hover:brightness-110 flex items-center justify-center gap-2"
          >
            <Sliders size={18} /> Get Started Customising
          </Link>
          <Link
            href="/cart"
            className="py-3 px-8 rounded-lg font-bold bg-surface-panel border border-white/10 text-text-primary hover:border-white/20 hover:bg-white/5 transition-all duration-300 flex items-center justify-center gap-2"
          >
            <ShoppingBag size={18} /> View Shopping Cart
          </Link>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full mt-10">
          <div className="p-6 rounded-xl glass-panel border-white/5 flex flex-col items-center text-center">
            <div className="w-12 h-12 rounded-lg bg-neon-pink/10 flex items-center justify-center mb-4 shadow-glow-pink">
              <Sliders className="text-neon-pink" size={22} />
            </div>
            <h3 className="font-bold text-lg mb-2">Schema-driven Engine</h3>
            <p className="text-text-muted text-xs leading-relaxed">
              Configure every element of your neon boards, frame sizes, and backings dynamically.
            </p>
          </div>

          <div className="p-6 rounded-xl glass-panel border-white/5 flex flex-col items-center text-center">
            <div className="w-12 h-12 rounded-lg bg-neon-blue/10 flex items-center justify-center mb-4 shadow-glow-blue">
              <Sparkles className="text-neon-blue" size={22} />
            </div>
            <h3 className="font-bold text-lg mb-2">AI-Powered Previews</h3>
            <p className="text-text-muted text-xs leading-relaxed">
              See what your custom neon boards look like immediately using AI visual approximation.
            </p>
          </div>

          <div className="p-6 rounded-xl glass-panel border-white/5 flex flex-col items-center text-center">
            <div className="w-12 h-12 rounded-lg bg-neon-violet/10 flex items-center justify-center mb-4 shadow-glow-violet">
              <CheckCircle2 className="text-neon-violet" size={22} />
            </div>
            <h3 className="font-bold text-lg mb-2">Checkout Handoff</h3>
            <p className="text-text-muted text-xs leading-relaxed">
              Submit your inquiry with verified price estimates. Checkout instantly without payment gateways.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}

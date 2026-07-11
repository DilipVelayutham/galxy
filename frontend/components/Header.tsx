'use client';

import React from 'react';
import Link from 'next/link';
import { useAuth } from '../context/AuthContext';
import { ShoppingCart, LogOut, LogIn, Sparkles } from 'lucide-react';

export default function Header() {
  const { user, logout, cartCount } = useAuth();

  return (
    <header className="sticky top-0 z-40 border-b border-white/5 bg-bg-void/85 backdrop-blur-md">
      <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2 group">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-neon-pink to-neon-violet flex items-center justify-center shadow-glow-pink">
            <Sparkles size={16} className="text-[#0B0B0F]" />
          </div>
          <span className="text-xl font-extrabold font-display tracking-wider text-glow-pink text-neon-pink animate-flicker group-hover:brightness-110 transition-all">
            GALXY
          </span>
        </Link>

        {/* Navigation Links */}
        <nav className="flex items-center gap-8">
          <Link
            href="/products/custom-neon-sign"
            className="text-sm font-semibold text-text-muted hover:text-neon-blue transition-colors duration-200"
          >
            Configurator
          </Link>
          <Link
            href="/cart"
            className="relative p-2 text-text-muted hover:text-neon-blue transition-colors duration-200 flex items-center gap-1"
          >
            <ShoppingCart size={18} />
            <span className="text-sm font-semibold hidden sm:inline">Cart</span>
            {cartCount > 0 && (
              <span className="absolute -top-1 -right-1 bg-neon-pink text-white text-[10px] font-bold w-5 h-5 rounded-full flex items-center justify-center border-2 border-bg-void shadow-glow-pink">
                {cartCount}
              </span>
            )}
          </Link>
        </nav>

        {/* Authentication Info */}
        <div className="flex items-center gap-4">
          {user ? (
            <div className="flex items-center gap-3.5 border-l border-white/10 pl-4">
              <div className="hidden md:flex flex-col text-right">
                <span className="text-[10px] text-text-muted font-bold uppercase tracking-wider">Customer Account</span>
                <span className="text-xs font-bold text-neon-violet text-glow-violet">{user.name}</span>
              </div>
              <button
                onClick={logout}
                className="p-2 text-text-muted hover:text-neon-pink transition-colors duration-200 flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider"
                title="Log Out"
              >
                <LogOut size={16} />
                <span className="hidden sm:inline">Logout</span>
              </button>
            </div>
          ) : (
            <Link
              href="/login"
              className="py-1.5 px-4 rounded-md bg-white/5 border border-white/10 text-xs font-bold text-text-primary hover:bg-white/10 hover:border-white/20 transition-all flex items-center gap-1.5"
            >
              <LogIn size={14} />
              Login
            </Link>
          )}
        </div>
      </div>
    </header>
  );
}

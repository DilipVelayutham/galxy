"use client";

import React from "react";
import { useCart } from "@/lib/cart-context";
import CountUp from "@/components/CountUp";
import { ShoppingCart } from "lucide-react";
import Image from "next/image";

interface ValidationError {
  item: string;
  reason: string;
}

interface CheckoutSummaryProps {
  validationErrors?: ValidationError[];
}

export default function CheckoutSummary({ validationErrors = [] }: CheckoutSummaryProps) {
  const { items, summary } = useCart();

  if (items.length === 0) {
    return (
      <div className="glass-panel p-6 rounded-3xl border border-white/5 text-center flex flex-col items-center justify-center py-12">
        <ShoppingCart className="h-10 w-10 text-slate-500 mb-3" />
        <p className="text-slate-400 text-sm font-bold">Your cart is empty</p>
      </div>
    );
  }

  return (
    <div className="glass-panel p-6 rounded-3xl border border-white/5 space-y-6 text-left">
      <h2 className="text-lg font-bold text-white flex items-center gap-2 pb-4 border-b border-white/5">
        <ShoppingCart className="h-5 w-5 text-indigo-400" />
        <span>Order Summary</span>
      </h2>

      {/* Cart Items List */}
      <div className="divide-y divide-white/5 max-h-[320px] overflow-y-auto pr-2 space-y-4">
        {items.map((item, idx) => {
          const matchingErrors = validationErrors.filter(
            (err) => err.item.toLowerCase() === item.name.toLowerCase()
          );
          
          return (
            <div key={item.id} className={`flex gap-4 pt-4 first:pt-0 ${idx > 0 ? "pt-4" : ""}`}>
              {/* Thumbnail */}
              <div className="h-16 w-16 rounded-xl overflow-hidden border border-white/5 bg-slate-900 shrink-0 relative">
                <Image
                  src={item.thumbnail}
                  alt={item.name}
                  className="h-full w-full object-cover"
                  width={64}
                  height={64}
                />
                <span className="absolute -top-1.5 -right-1.5 bg-indigo-600 text-white font-extrabold text-[10px] h-5 w-5 rounded-full flex items-center justify-center border border-[#090d16]">
                  {item.quantity}
                </span>
              </div>

              {/* Product Details */}
              <div className="flex-1 min-w-0">
                <h4 className="font-extrabold text-sm text-white truncate leading-snug">{item.name}</h4>
                
                {/* Configurations */}
                {Object.keys(item.configuration).length > 0 && (
                  <div className="mt-1 flex flex-wrap gap-x-2 gap-y-0.5">
                    {Object.entries(item.configuration).map(([key, val]) => (
                      <span key={key} className="text-[10px] font-medium text-slate-400 bg-white/5 px-1.5 py-0.5 rounded border border-white/5">
                        {key}: <span className="text-slate-300 font-semibold">{val}</span>
                      </span>
                    ))}
                  </div>
                )}
                
                {/* Price */}
                <div className="mt-1.5 text-xs text-indigo-400 font-extrabold">
                  <CountUp value={item.price} prefix="$" />
                  {item.quantity > 1 && (
                    <span className="text-slate-500 font-medium ml-1.5">
                      (each: ${item.price.toFixed(2)})
                    </span>
                  )}
                </div>

                {/* Item-specific Validation Errors */}
                {matchingErrors.length > 0 && (
                  <div className="mt-2.5 p-2.5 rounded-lg bg-red-500/10 border border-red-500/25 text-[10px] text-red-200 font-semibold space-y-1">
                    {matchingErrors.map((err, errIdx) => (
                      <div key={errIdx} className="leading-relaxed">
                        {err.reason}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Summary Totals (Backend values only, no frontend math) */}
      <div className="pt-6 border-t border-white/5 space-y-3 text-sm">
        <div className="flex items-center justify-between font-semibold text-slate-400">
          <span>Subtotal</span>
          <span className="text-slate-200">
            <CountUp value={summary.subtotal} prefix="$" />
          </span>
        </div>

        <div className="flex items-center justify-between font-semibold text-slate-400">
          <span>Shipping & Handling</span>
          {summary.shipping === 0 ? (
            <span className="text-green-400 font-bold">Free</span>
          ) : (
            <span className="text-slate-200">
              <CountUp value={summary.shipping} prefix="$" />
            </span>
          )}
        </div>

        <div className="flex items-center justify-between font-semibold text-slate-400">
          <span>Estimated Tax</span>
          <span className="text-slate-200">
            <CountUp value={summary.tax} prefix="$" />
          </span>
        </div>

        <div className="pt-3 border-t border-white/5 flex items-center justify-between text-base font-extrabold text-white">
          <span>Order Total</span>
          <span className="text-indigo-400 text-lg">
            <CountUp value={summary.total} prefix="$" />
          </span>
        </div>
      </div>
    </div>
  );
}

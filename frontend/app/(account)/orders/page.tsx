"use client";

import React, { useEffect, useState } from "react";
import { OrderHistoryItem, OrdersAPI } from "@/lib/api";
import OrderHistoryCard from "@/components/OrderHistoryCard";
import { ClipboardList, ShoppingBag, AlertCircle } from "lucide-react";
import Link from "next/link";

export default function OrderHistoryPage() {
  const [orders, setOrders] = useState<OrderHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadOrders() {
      try {
        const data = await OrdersAPI.getOrders();
        // Sort orders by created date descending
        const sorted = data.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
        setOrders(sorted);
      } catch (err) {
        console.error("Failed to load orders history", err);
        setError("Could not retrieve order history. Please try again.");
      } finally {
        setLoading(false);
      }
    }
    loadOrders();
  }, []);

  return (
    <div className="space-y-6 text-left pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-white/5">
        <div>
          <h1 className="text-2xl font-extrabold text-white tracking-wide">Order History</h1>
          <p className="text-xs text-slate-400 mt-1">Review status, track deliveries, and manage past purchases.</p>
        </div>
        <Link
          href="/checkout"
          className="px-5 py-2.5 rounded-xl text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-500 active:scale-95 transition-all shadow-md shadow-indigo-600/10 flex items-center gap-1.5 self-start sm:self-center"
        >
          <ShoppingBag className="h-4 w-4" />
          <span>New Order / Checkout</span>
        </Link>
      </div>

      {/* Main Content States */}
      {loading ? (
        // Loading skeleton list
        <div className="space-y-4">
          {[1, 2, 3].map((num) => (
            <div key={num} className="glass-panel p-5 sm:p-6 rounded-2xl border border-white/5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 animate-pulse">
              <div className="flex items-center gap-4 flex-1 w-full">
                {/* Image Skeleton */}
                <div className="h-16 w-16 sm:h-20 sm:w-20 rounded-xl bg-white/5 shrink-0" />
                
                {/* Details Skeleton */}
                <div className="flex-1 space-y-2">
                  <div className="flex items-center gap-2">
                    <div className="h-5 w-36 bg-white/10 rounded-md" />
                    <div className="h-5 w-16 bg-white/5 rounded-full" />
                  </div>
                  <div className="flex gap-4">
                    <div className="h-4 w-28 bg-white/5 rounded-md" />
                    <div className="h-4 w-12 bg-white/5 rounded-md" />
                  </div>
                </div>
              </div>
              
              {/* Right Skeleton */}
              <div className="flex sm:flex-col items-center sm:items-end justify-between sm:justify-center w-full sm:w-auto pt-3 sm:pt-0 border-t sm:border-t-0 border-white/5 gap-3 shrink-0">
                <div className="space-y-1.5 w-24 text-left sm:text-right">
                  <div className="h-3 w-12 bg-white/5 rounded-md ml-0 sm:ml-auto" />
                  <div className="h-5 w-20 bg-white/10 rounded-md ml-0 sm:ml-auto" />
                </div>
                <div className="h-8 w-8 rounded-full bg-white/5" />
              </div>
            </div>
          ))}
        </div>
      ) : error ? (
        // Error state
        <div className="glass-panel p-8 rounded-3xl border border-red-500/10 bg-red-500/5 text-center flex flex-col items-center justify-center space-y-4 max-w-md mx-auto">
          <AlertCircle className="h-10 w-10 text-red-400" />
          <div className="space-y-1">
            <h3 className="font-bold text-white text-base">Error Loading Orders</h3>
            <p className="text-xs text-slate-400 leading-relaxed">{error}</p>
          </div>
          <button
            onClick={() => {
              setLoading(true);
              setError(null);
              OrdersAPI.getOrders().then(setOrders).catch(err => setError(err.message)).finally(() => setLoading(false));
            }}
            className="px-5 py-2 rounded-lg bg-indigo-600 text-xs font-bold text-white hover:bg-indigo-500 transition-colors"
          >
            Retry Fetch
          </button>
        </div>
      ) : orders.length === 0 ? (
        // Empty state
        <div className="glass-panel p-12 rounded-3xl border border-white/5 text-center max-w-md mx-auto flex flex-col items-center justify-center space-y-4">
          <div className="h-14 w-14 rounded-full bg-white/5 flex items-center justify-center text-slate-400">
            <ClipboardList className="h-7 w-7" />
          </div>
          <div className="space-y-1">
            <h3 className="text-base font-bold text-white">No Orders Found</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              You haven&apos;t placed any purchases yet. Start shopping and head to the checkout page!
            </p>
          </div>
          <Link
            href="/checkout"
            className="px-5 py-2.5 rounded-xl text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-500 active:scale-95 transition-all shadow-md shadow-indigo-600/10"
          >
            Go to Checkout Page
          </Link>
        </div>
      ) : (
        // Order Cards list
        <div className="space-y-4">
          {orders.map((order) => (
            <OrderHistoryCard key={order.order_number} order={order} />
          ))}
        </div>
      )}
    </div>
  );
}

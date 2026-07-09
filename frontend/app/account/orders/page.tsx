"use client";

import React, { useState, useEffect } from "react";
import { api } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { useToast } from "@/context/ToastContext";
import { useRouter } from "next/navigation";
import { ClipboardList, ArrowRight, Loader2 } from "lucide-react";
import Link from "next/link";

interface Order {
  _id: string;
  order_number: string;
  estimated_total: number;
  final_quoted_price: number | null;
  status: string;
  created_at: string;
}

export default function OrderHistoryPage() {
  const { isAuthenticated, loading: authLoading } = useAuth();
  const { showToast } = useToast();
  const router = useRouter();

  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    if (!authLoading) {
      if (!isAuthenticated) {
        showToast("Please login to view your orders", "warning");
        router.push("/login");
        return;
      }
      
      const fetchOrders = async () => {
        try {
          const res = await api.get("/orders");
          if (res.success && res.data) {
            setOrders(res.data);
          }
        } catch {
          showToast("Error retrieving your orders tracking history", "error");
        } finally {
          setLoading(false);
        }
      };
      
      fetchOrders();
    }
  }, [isAuthenticated, authLoading, router, showToast]);

  const getStatusColorClass = (status: string) => {
    switch (status) {
      case "received": return "text-neon-blue border-neon-blue/30 bg-neon-blue/5";
      case "reviewed": return "text-neon-violet border-neon-violet/30 bg-neon-violet/5";
      case "production": return "text-neon-yellow border-neon-yellow/30 bg-neon-yellow/5";
      case "delivered": return "text-green-400 border-green-500/30 bg-green-500/5";
      case "cancelled": return "text-neon-pink border-neon-pink/30 bg-neon-pink/5";
      default: return "text-text-muted border-panel-charcoal bg-panel-charcoal/20";
    }
  };

  if (authLoading || loading) {
    return (
      <div className="min-h-screen bg-void-black flex flex-col items-center justify-center text-text-muted text-sm gap-2">
        <Loader2 className="w-8 h-8 animate-spin text-neon-blue" />
        <span>Loading order history timeline...</span>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-void-black text-text-primary p-6 md:p-10 selection:bg-neon-pink selection:text-void-black">
      <div className="max-w-4xl mx-auto flex flex-col gap-6">
        
        {/* Header */}
        <div className="border-b border-panel-charcoal pb-4">
          <h1 className="text-2xl font-black uppercase tracking-tight flex items-center gap-2">
            <ClipboardList className="w-6 h-6 text-neon-blue drop-shadow-[0_0_8px_#18E7FF]" />
            Order Inquiries
          </h1>
          <p className="text-xs text-text-muted mt-1">
            Track status updates, quote prices, and shipping tracking timelines for your custom lighting pieces.
          </p>
        </div>

        {orders.length === 0 ? (
          <div className="py-20 text-center rounded-xl bg-panel-charcoal/20 border border-panel-charcoal text-text-muted flex flex-col items-center gap-3">
            <ClipboardList className="w-12 h-12 opacity-35 text-neon-blue" />
            <p className="font-bold text-sm">No order inquiries found</p>
            <p className="text-xs">You have not submitted any custom design inquiries yet.</p>
            <Link
              href="/"
              className="mt-2 px-5 py-2.5 rounded bg-panel-charcoal hover:bg-void-black border border-neon-blue/40 text-neon-blue text-xs font-bold transition-all cursor-pointer"
            >
              START DESIGNING
            </Link>
          </div>
        ) : (
          <div className="flex flex-col gap-4">
            {orders.map((order) => (
              <div
                key={order._id}
                className="p-5 rounded-xl border border-panel-charcoal bg-panel-charcoal/20 flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between hover:border-panel-charcoal/80 transition-colors"
              >
                <div className="flex flex-col gap-1">
                  <div className="flex items-center gap-2.5">
                    <span className="font-extrabold text-sm text-text-primary">
                      Inquiry #{order.order_number}
                    </span>
                    <span className={`text-[10px] px-2 py-0.5 rounded-full border uppercase font-bold ${getStatusColorClass(order.status)}`}>
                      {order.status}
                    </span>
                  </div>
                  <span className="text-[10px] text-text-muted mt-1">
                    Submitted: {new Date(order.created_at).toLocaleDateString("en-IN", {
                      day: "numeric",
                      month: "short",
                      year: "numeric"
                    })}
                  </span>
                </div>

                <div className="flex items-center justify-between sm:justify-end gap-6 w-full sm:w-auto pt-3 sm:pt-0 border-t sm:border-t-0 border-panel-charcoal/45">
                  <div className="text-right">
                    <span className="text-[10px] text-text-muted block">Quoted Price</span>
                    <span className="text-sm font-black text-neon-blue">
                      {order.final_quoted_price !== null 
                        ? `₹${order.final_quoted_price.toLocaleString("en-IN")}` 
                        : "Awaiting Quote"}
                    </span>
                  </div>

                  <Link
                    href={`/account/orders/${order.order_number}`}
                    className="p-2.5 rounded bg-panel-charcoal hover:bg-void-black border border-panel-charcoal hover:border-neon-blue/40 text-text-muted hover:text-neon-blue transition-all cursor-pointer flex items-center justify-center"
                    title="Track Order Status"
                  >
                    <ArrowRight className="w-4 h-4" />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}

      </div>
    </div>
  );
}

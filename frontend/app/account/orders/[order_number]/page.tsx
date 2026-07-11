"use client";

import React, { useState, useEffect, use } from "react";
import { api } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { useToast } from "@/context/ToastContext";
import { useRouter } from "next/navigation";
import { StatusTracker } from "@/components/orders/StatusTracker";
import { ClipboardList, ArrowLeft, Loader2, IndianRupee, ShieldAlert } from "lucide-react";
import Link from "next/link";

interface OrderItem {
  product_id: string;
  product_title: string;
  category_name: string;
  selected_attributes: Record<string, any>;
  quantity: number;
  unit_price_estimate: number;
  ai_preview_image: string | null;
}

interface StatusHistoryEntry {
  status: string;
  note: string;
  timestamp: string;
  updated_by: string;
}

interface Order {
  _id: string;
  order_number: string;
  status: string;
  estimated_total: number;
  final_quoted_price: number | null;
  customer_visible_note: string;
  items: OrderItem[];
  status_history: StatusHistoryEntry[];
  created_at: string;
}

export default function OrderDetailPage({ params }: { params: Promise<{ order_number: string }> }) {
  const { order_number } = use(params);
  const { isAuthenticated, loading: authLoading } = useAuth();
  const { showToast } = useToast();
  const router = useRouter();

  const [order, setOrder] = useState<Order | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    if (!authLoading) {
      if (!isAuthenticated) {
        showToast("Please login to view order progress", "warning");
        router.push("/login");
        return;
      }

      const fetchOrder = async () => {
        try {
          const res = await api.get(`/orders/${order_number}`);
          if (res.success && res.data) {
            setOrder(res.data);
          } else {
            showToast(res.message || "Order tracking details not found", "error");
          }
        } catch {
          showToast("Network order retrieval error", "error");
        } finally {
          setLoading(false);
        }
      };

      fetchOrder();
    }
  }, [order_number, isAuthenticated, authLoading, router, showToast]);

  if (authLoading || loading) {
    return (
      <div className="min-h-screen bg-void-black flex flex-col items-center justify-center text-text-muted text-sm gap-2">
        <Loader2 className="w-8 h-8 animate-spin text-neon-blue" />
        <span>Loading milestone status updates...</span>
      </div>
    );
  }

  if (!order) {
    return (
      <div className="min-h-screen bg-void-black text-text-primary p-10 flex flex-col items-center justify-center gap-4">
        <h2 className="text-xl font-bold">Order Not Found</h2>
        <Link href="/account/orders" className="text-neon-blue underline text-xs">Return to Inquiries</Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-void-black text-text-primary p-6 md:p-10 selection:bg-neon-pink selection:text-void-black">
      <div className="max-w-4xl mx-auto flex flex-col gap-6">
        
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-panel-charcoal pb-4">
          <div>
            <Link
              href="/account/orders"
              className="inline-flex items-center gap-1.5 text-xs text-text-muted hover:text-neon-blue font-bold mb-3"
            >
              <ArrowLeft className="w-3.5 h-3.5" /> Back to Inquiries
            </Link>
            <h1 className="text-xl font-black uppercase tracking-tight flex items-center gap-2">
              <ClipboardList className="w-5 h-5 text-neon-blue" />
              Tracking Inquiry #{order.order_number}
            </h1>
          </div>

          <div className="flex flex-col sm:items-end">
            <span className="text-[10px] text-text-muted">Final Price Quoted</span>
            <span className="text-lg font-black text-neon-blue flex items-center gap-1 mt-0.5">
              <IndianRupee className="w-4 h-4" />
              {order.final_quoted_price !== null 
                ? order.final_quoted_price.toLocaleString("en-IN") 
                : "Awaiting Quote"}
            </span>
          </div>
        </div>

        {/* Tracking Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          
          {/* Tracking Timeline */}
          <div className="lg:col-span-8 flex flex-col gap-6">
            <div className="p-6 rounded-2xl bg-panel-charcoal/20 border border-panel-charcoal flex flex-col gap-6">
              <h3 className="text-sm font-bold text-text-primary uppercase tracking-wider border-b border-panel-charcoal/50 pb-3">
                Milestone Status timeline
              </h3>
              
              <StatusTracker currentStatus={order.status} history={order.status_history} />
            </div>

            {/* Note alert */}
            {order.customer_visible_note && (
              <div className="p-4 rounded-xl bg-neon-blue/5 border border-neon-blue/20 flex gap-3 items-start">
                <ShieldAlert className="w-5 h-5 text-neon-blue flex-shrink-0 mt-0.5" />
                <div>
                  <h4 className="text-xs font-bold text-neon-blue uppercase">Status Update Message</h4>
                  <p className="text-xs text-text-muted mt-1 leading-relaxed">
                    "{order.customer_visible_note}"
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* Inquiry summary list */}
          <div className="lg:col-span-4 p-6 rounded-2xl bg-panel-charcoal border border-panel-charcoal flex flex-col gap-4">
            <h3 className="text-sm font-bold uppercase tracking-wider text-text-primary border-b border-panel-charcoal/50 pb-2">
              Item Details
            </h3>

            <div className="flex flex-col gap-4 max-h-[350px] overflow-y-auto pr-1">
              {order.items.map((item, idx) => (
                <div key={idx} className="flex flex-col gap-2.5 border-b border-panel-charcoal/40 pb-3 last:border-b-0 last:pb-0">
                  <div className="flex gap-3">
                    <div className="w-12 h-12 rounded border border-panel-charcoal bg-void-black overflow-hidden flex-shrink-0">
                      <img src={item.ai_preview_image || "/file.svg"} alt="preview" className="w-full h-full object-cover" />
                    </div>
                    <div>
                      <h4 className="text-xs font-bold text-text-primary line-clamp-1">{item.product_title}</h4>
                      <span className="text-[9px] text-text-muted bg-void-black/50 px-1 rounded uppercase mt-0.5 inline-block">{item.category_name}</span>
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-1 text-[9px] text-text-muted">
                    {Object.entries(item.selected_attributes).map(([k, v]) => (
                      <span key={k} className="bg-void-black/30 px-1.5 py-0.5 rounded border border-panel-charcoal/45">
                        {k}: {String(v)}
                      </span>
                    ))}
                  </div>

                  <div className="flex justify-between items-baseline text-[10px] mt-1">
                    <span className="text-text-muted">Quantity: {item.quantity}</span>
                    <span className="font-black text-neon-blue">₹{(item.unit_price_estimate * item.quantity).toLocaleString("en-IN")}</span>
                  </div>
                </div>
              ))}
            </div>

            <div className="border-t border-panel-charcoal pt-4 mt-2 flex justify-between items-baseline text-xs">
              <span className="text-text-muted">Initial Estimated Total</span>
              <span className="font-black text-text-primary">₹{order.estimated_total.toLocaleString("en-IN")}</span>
            </div>
          </div>

        </div>

      </div>
    </div>
  );
}

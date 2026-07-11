"use client";

import React, { useState, useEffect, useCallback } from "react";
import { useAuth } from "@/context/AuthContext";
import { useToast } from "@/context/ToastContext";
import { api } from "@/lib/api";
import { useRouter } from "next/navigation";
import { Shield, Clipboard, Edit2, CheckCircle2, IndianRupee, Loader2, RefreshCw } from "lucide-react";
import Link from "next/link";

interface Order {
  _id: string;
  order_number: string;
  customer_snapshot: {
    name: string;
    email: string;
  };
  status: string;
  estimated_total: number;
  final_quoted_price: number | null;
  created_at: string;
}

interface Stats {
  total_orders: number;
  total_revenue: number;
  pending_inquiries: number;
  completed_orders: number;
}

export default function AdminDashboardPage() {
  const { user, loading: authLoading } = useAuth();
  const { showToast } = useToast();
  const router = useRouter();

  const [orders, setOrders] = useState<Order[]>([]);
  const [stats, setStats] = useState<Stats>({
    total_orders: 0,
    total_revenue: 0,
    pending_inquiries: 0,
    completed_orders: 0
  });
  const [loading, setLoading] = useState(true);

  // Modal / status modification states
  const [editingId, setEditingId] = useState<string | null>(null);
  const [selectedStatus, setSelectedStatus] = useState("received");
  const [statusNote, setStatusNote] = useState("");
  
  const [quotingId, setQuotingId] = useState<string | null>(null);
  const [quotedVal, setQuotedVal] = useState<string>("");

  const fetchDashboardData = useCallback(async () => {
    setLoading(true);
    try {
      // 1. Fetch dashboard stats
      const statsRes = await api.get("/admin/dashboard/stats");
      if (statsRes.success && statsRes.data) {
        setStats({
          total_orders: statsRes.data.total_orders || 0,
          total_revenue: statsRes.data.total_revenue || 0,
          pending_inquiries: statsRes.data.pending_inquiries || 0,
          completed_orders: statsRes.data.completed_orders || 0
        });
      }

      // 2. Fetch admin orders list
      const ordersRes = await api.get("/admin/orders?limit=25");
      if (ordersRes.success && ordersRes.data) {
        setOrders(ordersRes.data);
      }
    } catch {
      showToast("Error loading dashboard data", "error");
    } finally {
      setLoading(false);
    }
  }, [showToast]);

  // Auth routing security guard
  useEffect(() => {
    if (!authLoading) {
      if (!user) {
        router.push("/login");
      } else if (user.role !== "super_admin") {
        showToast("Super Admin access is required", "error");
        router.push("/");
      } else {
        fetchDashboardData();
      }
    }
  }, [user, authLoading, router, fetchDashboardData, showToast]);

  const handleUpdateStatus = async () => {
    if (!editingId) return;
    try {
      const res = await api.put(`/admin/orders/${editingId}/status`, {
        status: selectedStatus,
        note: statusNote
      });
      if (res.success) {
        showToast("Order status updated, notification sent to customer!", "success");
        setEditingId(null);
        setStatusNote("");
        fetchDashboardData();
      } else {
        showToast(res.message || "Failed to update status", "error");
      }
    } catch {
      showToast("Network order update failed", "error");
    }
  };

  const handleApplyQuote = async () => {
    if (!quotingId || !quotedVal) return;
    try {
      const res = await api.put(`/admin/orders/${quotingId}/quote`, {
        final_quoted_price: Number(quotedVal)
      });
      if (res.success) {
        showToast("Final quote price updated successfully!", "success");
        setQuotingId(null);
        setQuotedVal("");
        fetchDashboardData();
      } else {
        showToast(res.message || "Failed to set quote", "error");
      }
    } catch {
      showToast("Network quoting error", "error");
    }
  };

  if (authLoading || !user || user.role !== "super_admin") {
    return (
      <div className="min-h-screen bg-void-black flex flex-col items-center justify-center text-text-muted text-sm gap-2">
        <Loader2 className="w-8 h-8 animate-spin text-neon-blue" />
        <span>Authorizing Admin Access...</span>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-void-black text-text-primary p-6 md:p-10 selection:bg-neon-pink selection:text-void-black">
      <div className="max-w-6xl mx-auto flex flex-col gap-8">
        
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-panel-charcoal pb-5">
          <div>
            <h1 className="text-2xl font-black flex items-center gap-2 tracking-tight">
              <Shield className="w-6 h-6 text-neon-blue drop-shadow-[0_0_8px_#18E7FF]" />
              ADMIN CONTROL PANEL
            </h1>
            <p className="text-xs text-text-muted mt-1">
              Confirm order prices, trigger production timeline milestones, and moderate community reviews.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <Link
              href="/reviews"
              className="px-4 py-2.5 rounded bg-panel-charcoal hover:bg-void-black border border-neon-pink/30 hover:border-neon-pink/50 text-neon-pink text-xs font-bold transition-all cursor-pointer"
            >
              MODERATE REVIEWS
            </Link>
            <button
              onClick={fetchDashboardData}
              className="p-2.5 rounded bg-panel-charcoal border border-panel-charcoal/50 hover:border-neon-blue/40 text-text-muted hover:text-text-primary cursor-pointer transition-colors"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin text-neon-blue" : ""}`} />
            </button>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="p-5 rounded-xl border border-panel-charcoal bg-panel-charcoal/20">
            <span className="text-[10px] text-text-muted uppercase font-bold tracking-wider">Total Inquiries</span>
            <span className="text-2xl font-black text-neon-blue block mt-1">{stats.total_orders}</span>
          </div>
          <div className="p-5 rounded-xl border border-panel-charcoal bg-panel-charcoal/20">
            <span className="text-[10px] text-text-muted uppercase font-bold tracking-wider">Pending Quotes</span>
            <span className="text-2xl font-black text-neon-yellow block mt-1">{stats.pending_inquiries}</span>
          </div>
          <div className="p-5 rounded-xl border border-panel-charcoal bg-panel-charcoal/20">
            <span className="text-[10px] text-text-muted uppercase font-bold tracking-wider">Completed Orders</span>
            <span className="text-2xl font-black text-green-400 block mt-1">{stats.completed_orders}</span>
          </div>
          <div className="p-5 rounded-xl border border-panel-charcoal bg-panel-charcoal/20">
            <span className="text-[10px] text-text-muted uppercase font-bold tracking-wider">Total Revenue Flow</span>
            <span className="text-2xl font-black text-neon-violet block mt-1">₹{stats.total_revenue.toLocaleString("en-IN")}</span>
          </div>
        </div>

        {/* Orders Table */}
        <div className="rounded-2xl border border-panel-charcoal bg-panel-charcoal/20 overflow-hidden">
          <div className="p-5 border-b border-panel-charcoal/50 bg-panel-charcoal/10 flex items-center justify-between">
            <h3 className="text-sm font-bold uppercase tracking-wider text-text-primary">Custom Order Queue</h3>
          </div>

          {loading ? (
            <div className="py-20 text-center text-sm text-text-muted">Loading custom orders data...</div>
          ) : orders.length === 0 ? (
            <div className="py-16 text-center text-text-muted">No custom orders found.</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-panel-charcoal text-text-muted bg-panel-charcoal/20 font-bold">
                    <th className="p-4">Order #</th>
                    <th className="p-4">Customer</th>
                    <th className="p-4">Created At</th>
                    <th className="p-4">Est. Price</th>
                    <th className="p-4">Final Quote</th>
                    <th className="p-4">Status</th>
                    <th className="p-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {orders.map((o) => (
                    <tr key={o._id} className="border-b border-panel-charcoal/30 hover:bg-panel-charcoal/10 transition-colors">
                      <td className="p-4 font-bold text-text-primary">#{o.order_number}</td>
                      <td className="p-4">
                        <div className="flex flex-col">
                          <span className="font-semibold text-text-primary">{o.customer_snapshot?.name || "Client"}</span>
                          <span className="text-[9px] text-text-muted mt-0.5">{o.customer_snapshot?.email}</span>
                        </div>
                      </td>
                      <td className="p-4 text-text-muted">
                        {new Date(o.created_at).toLocaleDateString("en-IN", {
                          day: "numeric",
                          month: "short"
                        })}
                      </td>
                      <td className="p-4">₹{o.estimated_total.toLocaleString("en-IN")}</td>
                      <td className="p-4">
                        {o.final_quoted_price !== null ? (
                          <span className="font-bold text-neon-blue">₹{o.final_quoted_price.toLocaleString("en-IN")}</span>
                        ) : (
                          <span className="text-neon-yellow italic font-bold">Awaiting Quote</span>
                        )}
                      </td>
                      <td className="p-4">
                        <span className="px-2 py-0.5 rounded-full bg-panel-charcoal border border-panel-charcoal/80 uppercase font-bold text-[9px]">
                          {o.status}
                        </span>
                      </td>
                      <td className="p-4 text-right">
                        <div className="inline-flex gap-2">
                          <button
                            onClick={() => {
                              setQuotingId(o._id);
                              setQuotedVal(String(o.final_quoted_price || o.estimated_total));
                            }}
                            className="p-1.5 rounded border border-panel-charcoal hover:border-neon-blue text-text-muted hover:text-neon-blue cursor-pointer"
                            title="Set Quote Price"
                          >
                            <IndianRupee className="w-3.5 h-3.5" />
                          </button>
                          <button
                            onClick={() => {
                              setEditingId(o._id);
                              setSelectedStatus(o.status);
                            }}
                            className="p-1.5 rounded border border-panel-charcoal hover:border-neon-violet text-text-muted hover:text-neon-violet cursor-pointer"
                            title="Update Progress Status"
                          >
                            <Edit2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

      </div>

      {/* Quote Dialog */}
      {quotingId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-void-black/80 p-4">
          <div className="w-full max-w-sm p-6 rounded-xl glass-panel border border-neon-blue/30 flex flex-col gap-4 shadow-2xl">
            <h3 className="text-sm font-bold text-neon-blue uppercase">Set Final Quote Price</h3>
            <div className="flex flex-col gap-1">
              <label className="text-[10px] text-text-muted uppercase font-bold">Price Value (₹ INR)</label>
              <input
                type="number"
                value={quotedVal}
                onChange={(e) => setQuotedVal(e.target.value)}
                className="p-2.5 rounded bg-void-black border border-panel-charcoal text-sm text-text-primary focus:outline-none"
                placeholder="e.g. 7500"
              />
            </div>
            <div className="flex gap-3 justify-end mt-2">
              <button
                onClick={() => setQuotingId(null)}
                className="px-4 py-2 rounded bg-panel-charcoal text-xs text-text-muted font-bold hover:text-text-primary cursor-pointer"
              >
                Cancel
              </button>
              <button
                onClick={handleApplyQuote}
                className="px-4 py-2 rounded bg-neon-blue text-void-black text-xs font-black hover:bg-neon-blue/80 cursor-pointer"
              >
                Apply Price
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Status Transition Dialog */}
      {editingId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-void-black/80 p-4">
          <div className="w-full max-w-sm p-6 rounded-xl glass-panel border border-neon-violet/30 flex flex-col gap-4 shadow-2xl">
            <h3 className="text-sm font-bold text-neon-violet uppercase">Update Milestone Status</h3>
            
            <div className="flex flex-col gap-1.5">
              <label className="text-[10px] text-text-muted uppercase font-bold">New Status</label>
              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
                className="p-2.5 rounded bg-void-black border border-panel-charcoal text-xs text-text-primary focus:outline-none cursor-pointer"
              >
                <option value="received">Received</option>
                <option value="reviewed">Reviewed</option>
                <option value="quote_sent">Quote Sent</option>
                <option value="confirmed">Confirmed</option>
                <option value="in_production">In Production</option>
                <option value="ready">Ready</option>
                <option value="out_for_delivery">Out for Delivery</option>
                <option value="delivered">Delivered</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </div>

            <div className="flex flex-col gap-1.5">
              <label className="text-[10px] text-text-muted uppercase font-bold">Status Update Note</label>
              <textarea
                value={statusNote}
                onChange={(e) => setStatusNote(e.target.value)}
                className="p-2.5 rounded bg-void-black border border-panel-charcoal text-xs text-text-primary focus:outline-none"
                placeholder="Message visible to user tracking order timeline..."
                rows={3}
              />
            </div>

            <div className="flex gap-3 justify-end mt-2">
              <button
                onClick={() => setEditingId(null)}
                className="px-4 py-2 rounded bg-panel-charcoal text-xs text-text-muted font-bold hover:text-text-primary cursor-pointer"
              >
                Cancel
              </button>
              <button
                onClick={handleUpdateStatus}
                className="px-4 py-2 rounded bg-neon-violet text-void-black text-xs font-black hover:bg-neon-violet/80 cursor-pointer"
              >
                Update Milestone
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

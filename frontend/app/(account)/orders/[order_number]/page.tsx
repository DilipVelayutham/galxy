"use client";

import React, { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { OrderDetail, OrdersAPI } from "@/lib/api";
import StatusTracker from "@/components/StatusTracker";
import CountUp from "@/components/CountUp";
import { ChevronLeft, Calendar, FileText, MapPin, Truck, HelpCircle, PackageOpen, Copy, Check } from "lucide-react";
import Link from "next/link";
import Image from "next/image";

export default function OrderDetailPage() {
  const params = useParams();
  const orderNumber = params.order_number as string;

  const [order, setOrder] = useState<OrderDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  useEffect(() => {
    async function loadOrderDetails() {
      if (!orderNumber) return;
      try {
        const details = await OrdersAPI.getOrderDetails(orderNumber);
        setOrder(details);
      } catch (err: any) {
        console.error("Failed to load order detail details", err);
        if (err.response && err.response.status === 404) {
          setNotFound(true);
        } else {
          setError("Failed to load order information. Please reload the page.");
        }
      } finally {
        setLoading(false);
      }
    }
    loadOrderDetails();
  }, [orderNumber]);

  // Format date helper
  const formatDate = (isoString: string) => {
    const date = new Date(isoString);
    return date.toLocaleDateString(undefined, {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  // Status badge styling helper
  const getStatusBadgeStyle = (status: string) => {
    switch (status.toLowerCase()) {
      case "pending":
        return "bg-amber-500/10 border-amber-500/20 text-amber-400";
      case "confirmed":
        return "bg-blue-500/10 border-blue-500/20 text-blue-400";
      case "processing":
        return "bg-indigo-500/10 border-indigo-500/20 text-indigo-400";
      case "shipped":
        return "bg-purple-500/10 border-purple-500/20 text-purple-400";
      case "delivered":
        return "bg-green-500/10 border-green-500/20 text-green-400";
      case "cancelled":
        return "bg-red-500/10 border-red-500/20 text-red-400";
      default:
        return "bg-slate-500/10 border-slate-500/20 text-slate-400";
    }
  };

  if (loading) {
    return (
      <div className="space-y-6 text-left pb-12">
        <div className="h-6 w-32 bg-white/5 rounded-md animate-pulse" />
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          <div className="lg:col-span-8 space-y-6">
            <div className="h-64 bg-white/5 rounded-3xl animate-pulse" />
            <div className="h-44 bg-white/5 rounded-3xl animate-pulse" />
          </div>
          <div className="lg:col-span-4 h-[400px] bg-white/5 rounded-3xl animate-pulse" />
        </div>
      </div>
    );
  }

  // 404 Order Not Found Page
  if (notFound) {
    return (
      <div className="glass-panel p-10 rounded-3xl border border-white/5 text-center max-w-lg mx-auto flex flex-col items-center justify-center space-y-6 py-16 my-8 text-left">
        <div className="h-16 w-16 rounded-2xl bg-white/5 flex items-center justify-center text-red-400 border border-white/10 shadow-lg">
          <PackageOpen className="h-8 w-8" />
        </div>
        <div className="space-y-2">
          <h1 className="text-xl font-extrabold text-white">Order Not Found</h1>
          <p className="text-xs text-slate-400 leading-relaxed max-w-sm mx-auto">
            We couldn&apos;t find an order associated with the reference code <span className="font-extrabold text-slate-200">&quot;{orderNumber}&quot;</span> on your account profile.
          </p>
        </div>
        <Link
          href="/account/orders"
          className="px-6 py-3 rounded-xl text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-500 active:scale-95 transition-all shadow-md shadow-indigo-600/10 flex items-center gap-1.5"
        >
          <ChevronLeft className="h-4 w-4" />
          <span>Back to Order History</span>
        </Link>
      </div>
    );
  }

  if (error || !order) {
    return (
      <div className="glass-panel p-8 rounded-3xl border border-red-500/10 bg-red-500/5 text-center flex flex-col items-center justify-center space-y-4 max-w-md mx-auto my-8">
        <HelpCircle className="h-10 w-10 text-red-400" />
        <h3 className="font-bold text-white text-base">Error Loading Details</h3>
        <p className="text-xs text-slate-400 leading-relaxed">{error || "Failed to load order info."}</p>
        <Link
          href="/account/orders"
          className="px-5 py-2 rounded-lg bg-indigo-600 text-xs font-bold text-white hover:bg-indigo-500 transition-colors"
        >
          Return to History
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6 text-left pb-12">
      {/* Back link breadcrumb */}
      <div className="flex items-center justify-between pb-4 border-b border-white/5">
        <Link
          href="/account/orders"
          className="inline-flex items-center gap-1.5 text-xs font-bold text-slate-400 hover:text-white transition-colors"
        >
          <ChevronLeft className="h-4.5 w-4.5" />
          <span>Back to Orders</span>
        </Link>

        <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-white/5 border border-white/5 text-slate-400 select-none">
          Customer Portal
        </span>
      </div>

      {/* Hero Header Details */}
      <div className="glass-panel p-6 rounded-3xl border border-white/5 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div className="space-y-2">
          <div className="flex flex-wrap items-center gap-3">
            <span className="text-xl sm:text-2xl font-extrabold text-white tracking-wide">
              {order.order_number}
            </span>
            <button
              onClick={() => handleCopy(order.order_number)}
              className="p-1.5 hover:bg-white/5 rounded-lg text-slate-400 hover:text-white transition-colors flex items-center justify-center border border-white/5 bg-white/5"
              title="Copy Order Number"
            >
              {copied ? (
                <Check className="h-4 w-4 text-green-400" />
              ) : (
                <Copy className="h-4 w-4" />
              )}
            </button>
            <span className={`text-[10px] sm:text-xs font-extrabold px-3 py-0.5 rounded-full border uppercase tracking-wider ${getStatusBadgeStyle(order.status)}`}>
              {order.status}
            </span>
          </div>

          <div className="flex items-center gap-1.5 text-xs text-slate-400 font-semibold">
            <Calendar className="h-4 w-4 text-slate-500" />
            <span>Ordered on {formatDate(order.created_at)}</span>
          </div>
        </div>

        <div className="text-left md:text-right">
          <span className="block text-[10px] text-slate-500 font-bold uppercase tracking-wider">Total Amount Paid</span>
          <span className="text-2xl font-extrabold text-indigo-400">
            <CountUp value={order.total} prefix="$" />
          </span>
        </div>
      </div>

      {/* Customer visible note section if available */}
      {order.customer_visible_note && (
        <div className="glass-panel border-indigo-500/20 bg-indigo-500/5 p-5 rounded-2xl flex items-start gap-4">
          <FileText className="h-5 w-5 text-indigo-400 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <h4 className="text-xs font-bold text-slate-200">Latest Shipment Update Note</h4>
            <p className="text-xs text-slate-300 leading-relaxed font-medium">&quot;{order.customer_visible_note}&quot;</p>
          </div>
        </div>
      )}

      {/* Main split grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Side: Order items & Addresses */}
        <div className="lg:col-span-7 space-y-6">
          
          {/* Order Items */}
          <div className="glass-panel p-6 rounded-3xl border border-white/5 space-y-6">
            <h2 className="text-sm font-bold text-white flex items-center gap-2 pb-3 border-b border-white/5">
              <PackageOpen className="h-4.5 w-4.5 text-indigo-400" />
              <span>Ordered Items</span>
            </h2>

            <div className="divide-y divide-white/5 space-y-4">
              {order.items.map((item, idx) => (
                <div key={item.id} className={`flex gap-4 pt-4 first:pt-0 ${idx > 0 ? "pt-4" : ""}`}>
                  {/* Thumbnail */}
                  <div className="h-16 w-16 rounded-xl overflow-hidden border border-white/5 bg-slate-900 shrink-0">
                    <Image
                      src={item.thumbnail}
                      alt={item.name}
                      className="h-full w-full object-cover"
                      width={64}
                      height={64}
                    />
                  </div>

                  {/* Product details */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2">
                      <h4 className="font-extrabold text-sm text-white truncate leading-snug">{item.name}</h4>
                      <span className="text-xs text-slate-400 font-bold shrink-0">Qty: {item.quantity}</span>
                    </div>

                    {/* Configuration & Customizations */}
                    <div className="mt-2 space-y-1.5 text-left">
                      {Object.keys(item.configuration).length > 0 && (
                        <div className="flex flex-wrap gap-x-2 gap-y-0.5">
                          {Object.entries(item.configuration).map(([key, val]) => (
                            <span key={key} className="text-[9px] font-semibold text-slate-400 bg-white/5 px-1.5 py-0.5 rounded border border-white/5">
                              {key}: <span className="text-slate-300 font-bold">{val}</span>
                            </span>
                          ))}
                        </div>
                      )}

                      {/* Custom Text Option */}
                      {item.custom_text && (
                        <div className="text-[10px] text-indigo-400 bg-indigo-500/5 border border-indigo-500/10 px-2 py-1 rounded-md inline-flex items-center gap-1.5 max-w-full font-medium">
                          <span className="text-slate-500 font-semibold uppercase text-[8px] tracking-wider bg-white/5 px-1 py-0.5 rounded">Custom Text</span>
                          <span className="truncate italic font-semibold text-slate-200">&quot;{item.custom_text}&quot;</span>
                        </div>
                      )}

                      {/* Preview Image Option */}
                      {item.preview_image && (
                        <div className="mt-2 flex items-center gap-2">
                          <span className="text-[9px] text-slate-500 font-bold uppercase tracking-wider">Preview Image:</span>
                          <div className="relative group/preview h-12 w-12 rounded-lg overflow-hidden border border-white/10 bg-slate-950 shrink-0">
                            <Image
                              src={item.preview_image}
                              alt="Reference Image"
                              className="h-full w-full object-cover group-hover/preview:scale-110 transition-transform duration-200"
                              width={48}
                              height={48}
                            />
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Price */}
                    <div className="mt-1.5 text-xs text-indigo-400 font-extrabold">
                      <CountUp value={item.price} prefix="$" />
                      {item.quantity > 1 && (
                        <span className="text-slate-500 font-medium ml-1.5">
                          (each: ${item.price.toFixed(2)})
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Delivery Details */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            
            {/* Delivery address */}
            <div className="glass-panel p-6 rounded-3xl border border-white/5 space-y-4">
              <h2 className="text-xs font-bold text-white flex items-center gap-1.5">
                <MapPin className="h-4.5 w-4.5 text-indigo-400" />
                <span>Delivery Address</span>
              </h2>
              <div className="text-xs text-slate-300 space-y-1.5 leading-relaxed">
                <span className="font-extrabold text-white block mb-2">{order.address.recipient_name}</span>
                <p>
                  {order.address.street}
                  <br />
                  {order.address.city}, {order.address.state} {order.address.postal_code}
                  <br />
                  {order.address.country}
                </p>
                <span className="block pt-2 text-[10px] text-slate-500 font-semibold">{order.address.recipient_phone}</span>
              </div>
            </div>

            {/* Price breakdown */}
            <div className="glass-panel p-6 rounded-3xl border border-white/5 space-y-3">
              <h2 className="text-xs font-bold text-white flex items-center gap-1.5 pb-2 border-b border-white/5">
                <FileText className="h-4.5 w-4.5 text-indigo-400" />
                <span>Price Breakdown</span>
              </h2>
              <div className="text-xs space-y-2 text-slate-400">
                <div className="flex items-center justify-between font-semibold">
                  <span>Subtotal</span>
                  <span className="text-slate-200">
                    <CountUp value={order.subtotal} prefix="$" />
                  </span>
                </div>
                <div className="flex items-center justify-between font-semibold">
                  <span>Shipping</span>
                  <span className="text-slate-200">
                    <CountUp value={order.shipping} prefix="$" />
                  </span>
                </div>
                <div className="flex items-center justify-between font-semibold">
                  <span>Tax</span>
                  <span className="text-slate-200">
                    <CountUp value={order.tax} prefix="$" />
                  </span>
                </div>
                <div className="pt-2 border-t border-white/5 flex items-center justify-between font-extrabold text-white text-sm">
                  <span>Total Amount</span>
                  <span className="text-indigo-400">
                    <CountUp value={order.total} prefix="$" />
                  </span>
                </div>
              </div>
            </div>

          </div>
        </div>

        {/* Right Side: Animated Status Tracker */}
        <div className="lg:col-span-5 glass-panel p-6 rounded-3xl border border-white/5 space-y-6">
          <h2 className="text-sm font-bold text-white flex items-center gap-2 pb-3 border-b border-white/5">
            <Truck className="h-4.5 w-4.5 text-indigo-400" />
            <span>Shipment Status Tracker</span>
          </h2>

          <StatusTracker 
            statusHistory={order.status_history} 
            currentStatus={order.status} 
            customerVisibleNote={order.customer_visible_note} 
          />
        </div>
      </div>
    </div>
  );
}

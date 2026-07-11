"use client";

import React from "react";
import Link from "next/link";
import { OrderHistoryItem } from "@/lib/api";
import CountUp from "@/components/CountUp";
import { Calendar, ChevronRight } from "lucide-react";
import Image from "next/image";

interface OrderHistoryCardProps {
  order: OrderHistoryItem;
}

export default function OrderHistoryCard({ order }: OrderHistoryCardProps) {
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

  const formatDate = (isoString: string) => {
    const date = new Date(isoString);
    return date.toLocaleDateString(undefined, {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  return (
    <Link href={`/account/orders/${order.order_number}`} className="block group">
      <div className="glass-panel p-5 sm:p-6 rounded-2xl border border-white/5 hover:border-indigo-500/30 hover:bg-white/10 hover:shadow-lg hover:shadow-indigo-500/5 transition-all duration-300 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 text-left">
        <div className="flex items-center gap-4 flex-1 min-w-0">
          {/* First Item Thumbnail */}
          <div className="h-16 w-16 sm:h-20 sm:w-20 rounded-xl overflow-hidden border border-white/5 bg-slate-900 shrink-0">
            {order.first_item_thumbnail ? (
              <Image
                src={order.first_item_thumbnail}
                alt={order.order_number}
                className="h-full w-full object-cover group-hover:scale-105 transition-transform duration-300"
                width={80}
                height={80}
              />
            ) : (
              <div className="h-full w-full bg-slate-800 flex items-center justify-center text-xs text-slate-500">
                No Img
              </div>
            )}
          </div>

          {/* Details */}
          <div className="flex-1 min-w-0 space-y-1.5">
            <div className="flex flex-wrap items-center gap-2">
              <span className="font-extrabold text-sm sm:text-base text-white tracking-wide truncate">
                {order.order_number}
              </span>
              <span className={`text-[10px] sm:text-xs font-bold px-2.5 py-0.5 rounded-full border uppercase ${getStatusBadgeStyle(order.status)}`}>
                {order.status}
              </span>
            </div>

            <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-400 font-medium">
              <span className="flex items-center gap-1">
                <Calendar className="h-3.5 w-3.5 text-slate-500" />
                {formatDate(order.created_at)}
              </span>
              <span>
                {order.item_count} {order.item_count === 1 ? "item" : "items"}
              </span>
            </div>
          </div>
        </div>

        {/* Right Info: Total and link chevron */}
        <div className="flex sm:flex-col items-center sm:items-end justify-between sm:justify-center w-full sm:w-auto pt-3 sm:pt-0 border-t sm:border-t-0 border-white/5 gap-3">
          <div className="text-left sm:text-right">
            <span className="block text-[10px] text-slate-500 font-bold uppercase tracking-wider">Total Amount</span>
            <span className="text-base sm:text-lg font-extrabold text-indigo-400 group-hover:text-indigo-300 transition-colors">
              <CountUp value={order.total} prefix="$" />
            </span>
          </div>
          <div className="h-8 w-8 rounded-full bg-white/5 group-hover:bg-indigo-600 group-hover:text-white flex items-center justify-center text-slate-400 transition-all duration-300">
            <ChevronRight className="h-4.5 w-4.5 group-hover:translate-x-0.5 transition-transform" />
          </div>
        </div>
      </div>
    </Link>
  );
}

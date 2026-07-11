"use client";

import React from "react";
import { motion, useReducedMotion } from "framer-motion";
import { Check, ClipboardList, CheckCircle2, Package, Truck, Smile, XCircle } from "lucide-react";
import { StatusHistoryEvent } from "@/lib/api";

interface StatusTrackerProps {
  statusHistory: StatusHistoryEvent[];
  currentStatus: string;
  customerVisibleNote?: string;
}

export default function StatusTracker({ statusHistory, currentStatus, customerVisibleNote }: StatusTrackerProps) {
  const shouldReduceMotion = useReducedMotion();
  const [isMounted, setIsMounted] = React.useState(false);

  React.useEffect(() => {
    setIsMounted(true);
  }, []);

  const reduced = isMounted ? (shouldReduceMotion ?? false) : false;

  // Find the last completed event to attach the customer visible note to
  const completedEvents = statusHistory.filter((h) => h.completed);
  const latestCompletedEvent = completedEvents[completedEvents.length - 1];

  // Helper to choose stage icons based on the status name
  const getStatusIcon = (status: string, isCompleted: boolean) => {
    const iconClass = `h-5 w-5 ${isCompleted ? "text-white" : "text-slate-500"}`;
    switch (status.toLowerCase()) {
      case "pending":
        return <ClipboardList className={iconClass} />;
      case "confirmed":
        return <CheckCircle2 className={iconClass} />;
      case "processing":
        return <Package className={iconClass} />;
      case "shipped":
        return <Truck className={iconClass} />;
      case "delivered":
        return <Smile className={iconClass} />;
      case "cancelled":
        return <XCircle className="h-5 w-5 text-red-500" />;
      default:
        return <Check className={iconClass} />;
    }
  };

  // Helper for status styling classes
  const getStageColor = (status: string, isCompleted: boolean) => {
    if (status.toLowerCase() === "cancelled") {
      return {
        bg: "bg-red-500/10 border-red-500/30 shadow-red-500/10",
        indicator: "bg-red-500",
        text: "text-red-400"
      };
    }
    if (isCompleted) {
      return {
        bg: "bg-indigo-500/15 border-indigo-500/40 shadow-indigo-500/20",
        indicator: "bg-gradient-to-tr from-indigo-500 to-purple-500",
        text: "text-indigo-400"
      };
    }
    return {
      bg: "bg-slate-900/40 border-white/5 shadow-none",
      indicator: "bg-slate-800 border border-slate-700",
      text: "text-slate-500"
    };
  };

  // Format date helper
  const formatDate = (isoString: string) => {
    if (!isoString) return "";
    const date = new Date(isoString);
    return date.toLocaleDateString(undefined, {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <div className="relative flex flex-col space-y-8 pl-4 pr-2">
      {/* Animated Connector Line */}
      <div className="absolute left-[33px] top-6 bottom-6 w-0.5 bg-slate-800" />
      
      {/* Active Connector Progress Line */}
      {statusHistory.length > 1 && (
        <div className="absolute left-[33px] top-6 bottom-6 w-0.5 overflow-hidden">
          <motion.div
            className="w-full bg-gradient-to-b from-indigo-500 via-purple-500 to-pink-500 origin-top h-full"
            initial={{ scaleY: reduced ? 1 : 0 }}
            animate={{ 
              scaleY: (() => {
                const completedCount = statusHistory.filter(h => h.completed).length;
                if (completedCount <= 1) return 0;
                return (completedCount - 1) / (statusHistory.length - 1);
              })() 
            }}
            transition={{ duration: 1.2, ease: "easeInOut" }}
          />
        </div>
      )}

      {/* Tracker Steps */}
      {statusHistory.map((step, idx) => {
        const isCompleted = step.completed;
        const colors = getStageColor(step.status, isCompleted);
        const hasTimestamp = !!step.timestamp;
        const isLatestCompleted = latestCompletedEvent && latestCompletedEvent.status === step.status;

        // Parent container motion variants
        const containerVariants = {
          hidden: { opacity: 0, x: reduced ? 0 : -10 },
          visible: { 
            opacity: 1, 
            x: 0,
            transition: { 
              duration: 0.5, 
              delay: idx * 0.15,
              ease: "easeOut" as const
            }
          }
        };

        // Icon circle motion variants
        const circleVariants = {
          hidden: { scale: reduced ? 1 : 0.8 },
          visible: { 
            scale: 1,
            transition: { 
              type: "spring" as const, 
              stiffness: 260, 
              damping: 20, 
              delay: idx * 0.15 
            }
          }
        };

        return (
          <motion.div
            key={idx}
            className="relative flex items-start gap-6 group text-left"
            initial="hidden"
            animate="visible"
            variants={containerVariants}
          >
            {/* Stage Indicator Node */}
            <motion.div 
              className={`relative z-10 flex h-10 w-10 shrink-0 items-center justify-center rounded-full shadow-lg transition-shadow duration-300 ${colors.indicator}`}
              variants={circleVariants}
            >
              {getStatusIcon(step.status, isCompleted)}
              
              {/* Completed pulsing glow ring */}
              {isCompleted && step.status.toLowerCase() !== "cancelled" && (
                <div className="absolute inset-0 rounded-full bg-indigo-500/20 animate-ping opacity-75 -z-10" style={{ animationDuration: "3s" }} />
              )}
            </motion.div>

            {/* Stage Card */}
            <div className={`flex-1 glass-panel p-5 rounded-2xl border transition-all duration-300 ${isCompleted ? "border-white/10 hover:border-white/20" : "border-white/5 opacity-50"} ${colors.bg}`}>
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <h3 className={`font-bold text-sm sm:text-base ${isCompleted ? "text-white" : "text-slate-400"}`}>
                  {step.title}
                </h3>
                {hasTimestamp && (
                  <span className="text-[11px] font-medium px-2 py-0.5 rounded-full bg-white/5 border border-white/5 text-slate-400 self-start sm:self-center">
                    {formatDate(step.timestamp)}
                  </span>
                )}
              </div>
              <p className={`mt-2 text-xs sm:text-sm leading-relaxed ${isCompleted ? "text-slate-300" : "text-slate-500"}`}>
                {step.description}
              </p>

              {/* Latest Customer Visible Note Embedded */}
              {isLatestCompleted && customerVisibleNote && (
                <div className="mt-3 p-3 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-xs text-indigo-300 font-semibold leading-relaxed italic">
                  &quot;{customerVisibleNote}&quot;
                </div>
              )}
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}

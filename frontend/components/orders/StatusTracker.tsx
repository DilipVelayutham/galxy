"use client";

import React from "react";
import { Check, Package, Eye, FileText, Settings, Sparkles, CheckCircle2, Truck, Gift, XOctagon } from "lucide-react";

interface StatusHistoryItem {
  status: string;
  note: string;
  timestamp: string;
  updated_by?: string;
}

interface StatusTrackerProps {
  currentStatus: string;
  history: StatusHistoryItem[];
  accentColor?: "pink" | "blue" | "violet" | "yellow";
}

const STAGES = [
  { key: "received", label: "Inquiry Received", icon: Package },
  { key: "reviewed", label: "Details Reviewed", icon: Eye },
  { key: "quote_sent", label: "Price Quote Sent", icon: FileText },
  { key: "confirmed", label: "Inquiry Confirmed", icon: Check },
  { key: "in_production", label: "In Production", icon: Settings },
  { key: "ready", label: "Ready to Dispatch", icon: Sparkles },
  { key: "out_for_delivery", label: "Out for Delivery", icon: Truck },
  { key: "delivered", label: "Handed Over & Delivered", icon: Gift },
];

export const StatusTracker: React.FC<StatusTrackerProps> = ({
  currentStatus,
  history,
  accentColor = "blue",
}) => {
  const isCancelled = currentStatus === "cancelled";
  
  // Find current index in stages list
  const currentStageIndex = STAGES.findIndex((s) => s.key === currentStatus);

  // Map accents to styles
  const colorMap = {
    pink: { text: "text-neon-pink", bg: "bg-neon-pink", border: "border-neon-pink", shadow: "drop-shadow-[0_0_8px_#FF2E8A]" },
    blue: { text: "text-neon-blue", bg: "bg-neon-blue", border: "border-neon-blue", shadow: "drop-shadow-[0_0_8px_#18E7FF]" },
    violet: { text: "text-neon-violet", bg: "bg-neon-violet", border: "border-neon-violet", shadow: "drop-shadow-[0_0_8px_#9B5CFF]" },
    yellow: { text: "text-neon-yellow", bg: "bg-neon-yellow", border: "border-neon-yellow", shadow: "drop-shadow-[0_0_8px_#FFD84D]" }
  };

  const activeStyles = colorMap[accentColor] || colorMap.blue;

  const formatDate = (isoString: string) => {
    try {
      const d = new Date(isoString);
      return d.toLocaleDateString("en-IN", {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return "";
    }
  };

  return (
    <div className="p-6 rounded-xl glass-panel border border-panel-charcoal">
      <h3 className="text-lg font-bold text-text-primary mb-8 border-b border-panel-charcoal pb-3">
        Inquiry Status Tracker
      </h3>

      {isCancelled ? (
        <div className="flex gap-4 items-start p-4 rounded-lg border border-neon-pink/30 bg-neon-pink/5 mb-6">
          <XOctagon className="w-6 h-6 text-neon-pink flex-shrink-0 drop-shadow-[0_0_8px_#FF2E8A]" />
          <div>
            <h4 className="font-bold text-sm text-neon-pink">Order Inquiry Cancelled</h4>
            <p className="text-xs text-text-muted mt-1">
              {history.find((h) => h.status === "cancelled")?.note || "This order inquiry has been cancelled."}
            </p>
          </div>
        </div>
      ) : null}

      <div className="relative pl-10 flex flex-col gap-8">
        {/* Timeline Connecting line */}
        <div className="absolute top-3 left-4 bottom-3 w-0.5 bg-panel-charcoal" />
        
        {/* Active connecting line fill */}
        {!isCancelled && currentStageIndex >= 0 && (
          <div
            className={`absolute top-3 left-4 w-0.5 ${activeStyles.bg} transition-all duration-1000`}
            style={{
              height: `${(currentStageIndex / (STAGES.length - 1)) * 100}%`,
              maxHeight: "97%",
            }}
          />
        )}

        {STAGES.map((stage, idx) => {
          const isCompleted = !isCancelled && idx <= currentStageIndex;
          const isCurrent = !isCancelled && idx === currentStageIndex;
          const Icon = stage.icon;
          
          // Find matching entry in status_history
          const historyEntry = history.find((h) => h.status === stage.key);

          return (
            <div key={stage.key} className="relative flex flex-col items-start">
              {/* Timeline dot */}
              <div
                className={`absolute -left-[34px] top-1 w-6 h-6 rounded-full flex items-center justify-center border-2 z-10 transition-all duration-300 ${
                  isCompleted
                    ? `${activeStyles.bg} ${activeStyles.border} text-void-black ${activeStyles.shadow}`
                    : "bg-void-black border-panel-charcoal text-text-muted"
                }`}
              >
                {isCompleted && !isCurrent ? (
                  <Check className="w-3.5 h-3.5 stroke-[3]" />
                ) : (
                  <Icon className="w-3 h-3" />
                )}
              </div>

              {/* Stage Details */}
              <div className="flex flex-col gap-1">
                <span
                  className={`text-sm font-bold transition-colors ${
                    isCompleted ? activeStyles.text : "text-text-muted"
                  } ${isCurrent ? "text-glow-" + accentColor : ""}`}
                >
                  {stage.label}
                </span>

                {/* History timestamp */}
                {historyEntry && (
                  <span className="text-[10px] text-text-muted font-semibold">
                    {formatDate(historyEntry.timestamp)}
                  </span>
                )}

                {/* Status custom visible comment */}
                {historyEntry?.note && (
                  <p className="text-xs text-text-muted leading-relaxed mt-0.5 bg-panel-charcoal/20 p-2 rounded max-w-lg border border-panel-charcoal/40">
                    {historyEntry.note}
                  </p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

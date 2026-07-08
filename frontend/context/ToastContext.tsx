"use client";

import React, { createContext, useContext, useState, useCallback } from "react";
import { X, CheckCircle, AlertTriangle, Info } from "lucide-react";
import { AnimatePresence, motion } from "framer-motion";

export type ToastType = "success" | "error" | "info" | "warning";

export interface Toast {
  id: string;
  message: string;
  type: ToastType;
  duration?: number;
}

interface ToastContextType {
  toasts: Toast[];
  showToast: (message: string, type?: ToastType, duration?: number) => void;
  removeToast: (id: string) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const showToast = useCallback((message: string, type: ToastType = "info", duration = 4000) => {
    const id = Math.random().toString(36).substring(2, 9);
    setToasts((prev) => [...prev, { id, message, type, duration }]);
    
    setTimeout(() => {
      removeToast(id);
    }, duration);
  }, [removeToast]);

  return (
    <ToastContext.Provider value={{ toasts, showToast, removeToast }}>
      {children}
      
      {/* Toast container overlay */}
      <div className="fixed bottom-5 right-5 z-50 flex flex-col gap-3 w-full max-w-sm pointer-events-none">
        <AnimatePresence>
          {toasts.map((toast) => (
            <motion.div
              key={toast.id}
              initial={{ opacity: 0, y: 50, scale: 0.9 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              className={`p-4 rounded-xl border glass-panel pointer-events-auto flex items-start gap-3 shadow-xl ${
                toast.type === "success" ? "border-neon-blue/30" :
                toast.type === "error" ? "border-neon-pink/30" :
                toast.type === "warning" ? "border-neon-yellow/30" :
                "border-neon-violet/30"
              }`}
            >
              {/* Type icon */}
              <div className="mt-0.5">
                {toast.type === "success" && <CheckCircle className="w-5 h-5 text-neon-blue drop-shadow-[0_0_8px_#18E7FF]" />}
                {toast.type === "error" && <AlertTriangle className="w-5 h-5 text-neon-pink drop-shadow-[0_0_8px_#FF2E8A]" />}
                {toast.type === "warning" && <AlertTriangle className="w-5 h-5 text-neon-yellow drop-shadow-[0_0_8px_#FFD84D]" />}
                {toast.type === "info" && <Info className="w-5 h-5 text-neon-violet drop-shadow-[0_0_8px_#9B5CFF]" />}
              </div>

              {/* Message text */}
              <div className="flex-1 text-sm font-medium text-text-primary">
                {toast.message}
              </div>

              {/* Close button */}
              <button
                onClick={() => removeToast(toast.id)}
                className="text-text-muted hover:text-text-primary transition-colors cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </ToastContext.Provider>
  );
};

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error("useToast must be used within a ToastProvider");
  }
  return context;
};

"use client";

import { AlertTriangle } from "lucide-react";
import { useFocusTrap } from "../../../hooks/useFocusTrap";

interface DeleteConfirmDialogProps {
  open: boolean;
  title: string;
  description: string;
  loading: boolean;
  onClose: () => void;
  onConfirm: () => Promise<void> | void;
}

export function DeleteConfirmDialog({ open, title, description, loading, onClose, onConfirm }: DeleteConfirmDialogProps) {
  const containerRef = useFocusTrap(open, onClose);

  if (!open) return null;

  return (
    <div
      ref={containerRef}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="delete-dialog-title"
    >
      <div className="w-full max-w-md rounded-2xl border border-red-400/20 bg-[#16161C] p-5 text-white shadow-2xl">
        <div className="flex gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-red-400/10 text-red-300">
            <AlertTriangle className="h-5 w-5" aria-hidden="true" />
          </div>
          <div>
            <h2 id="delete-dialog-title" className="text-lg font-semibold">
              {title}
            </h2>
            <p className="mt-2 text-sm text-slate-300">{description}</p>
          </div>
        </div>
        <div className="mt-5 flex justify-end gap-2">
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg px-4 py-2 text-sm text-slate-300 hover:bg-white/5 focus:outline-none focus:ring-2 focus:ring-slate-500"
          >
            Cancel
          </button>
          <button
            type="button"
            disabled={loading}
            onClick={onConfirm}
            className="rounded-lg bg-red-400 px-4 py-2 text-sm font-semibold text-slate-950 focus:outline-none focus:ring-2 focus:ring-red-300 disabled:opacity-60"
          >
            {loading ? "Deleting..." : "Delete permanently"}
          </button>
        </div>
      </div>
    </div>
  );
}

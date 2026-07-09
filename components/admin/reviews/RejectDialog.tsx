"use client";

import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import type { Review } from "../../../types/review";
import { useFocusTrap } from "../../../hooks/useFocusTrap";
import { rejectSchema } from "../../../utils/validators";

interface RejectDialogProps {
  review: Review | null;
  loading: boolean;
  onClose: () => void;
  onConfirm: (reviewId: string, reason?: string) => Promise<void>;
}

interface RejectFormValues {
  reason?: string;
}

export function RejectDialog({ review, loading, onClose, onConfirm }: RejectDialogProps) {
  const containerRef = useFocusTrap(Boolean(review), onClose);

  const {
    handleSubmit,
    register,
    reset,
    setFocus,
    formState: { errors },
  } = useForm<RejectFormValues>({
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    resolver: zodResolver(rejectSchema) as any,
    defaultValues: { reason: "" },
  });

  useEffect(() => {
    if (review) {
      reset({ reason: "" });
      const focusTimer = window.setTimeout(() => setFocus("reason"), 0);
      return () => window.clearTimeout(focusTimer);
    }
    return undefined;
  }, [reset, review, setFocus]);

  if (!review) return null;

  return (
    <div
      ref={containerRef}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="reject-review-title"
    >
      <form
        onSubmit={handleSubmit(async ({ reason }) => {
          await onConfirm(review._id, reason?.trim() || undefined);
          onClose();
        })}
        className="w-full max-w-md rounded-2xl border border-white/10 bg-[#16161C] p-5 text-white shadow-2xl"
      >
        <h2 id="reject-review-title" className="text-lg font-semibold">
          Reject review
        </h2>
        <p className="mt-2 text-sm text-slate-400">
          Add an optional reason for rejecting {review.customer_name}&apos;s review.
        </p>
        <textarea
          {...register("reason")}
          rows={4}
          className="mt-4 w-full rounded-xl border border-white/10 bg-[#0B0B0F] p-3 text-sm outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20"
          placeholder="Optional reason"
        />
        {errors.reason?.message && <span className="text-xs text-red-300 mt-1 block">{errors.reason.message}</span>}
        <div className="mt-5 flex justify-end gap-2">
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg px-4 py-2 text-sm text-slate-300 hover:bg-white/5 focus:outline-none focus:ring-2 focus:ring-slate-500"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading}
            className="rounded-lg bg-amber-400 px-4 py-2 text-sm font-semibold text-slate-950 focus:outline-none focus:ring-2 focus:ring-amber-300 disabled:opacity-60"
          >
            {loading ? "Rejecting..." : "Reject"}
          </button>
        </div>
      </form>
    </div>
  );
}

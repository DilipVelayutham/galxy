"use client";

import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import type { PromoteReviewPayload, Review } from "../../../types/review";
import { useFocusTrap } from "../../../hooks/useFocusTrap";
import { promoteSchema } from "../../../utils/validators";

interface PromoteDialogProps {
  review: Review | null;
  loading: boolean;
  onClose: () => void;
  onConfirm: (reviewId: string, payload: PromoteReviewPayload) => Promise<void>;
}

export function PromoteDialog({ review, loading, onClose, onConfirm }: PromoteDialogProps) {
  const containerRef = useFocusTrap(Boolean(review), onClose);

  const {
    formState: { errors },
    handleSubmit,
    register,
    reset,
    setFocus,
  } = useForm<PromoteReviewPayload>({
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    resolver: zodResolver(promoteSchema) as any,
    defaultValues: { customer_location: "", display_order: undefined },
  });

  useEffect(() => {
    if (review) {
      reset({ customer_location: "", display_order: undefined });
      const focusTimer = window.setTimeout(() => setFocus("customer_location"), 0);
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
      aria-labelledby="promote-review-title"
    >
      <form
        onSubmit={handleSubmit(async (values) => {
          const payload: PromoteReviewPayload = {};
          const customerLocation = values.customer_location?.trim();

          if (customerLocation) payload.customer_location = customerLocation;
          else payload.customer_location = undefined;

          if (typeof values.display_order === "number" && Number.isFinite(values.display_order)) {
            payload.display_order = values.display_order;
          } else {
            payload.display_order = undefined;
          }

          await onConfirm(review._id, payload);
          onClose();
        })}
        className="w-full max-w-md rounded-2xl border border-white/10 bg-[#16161C] p-5 text-white shadow-2xl"
      >
        <h2 id="promote-review-title" className="text-lg font-semibold">
          Promote to testimonial
        </h2>
        <p className="mt-2 text-sm text-slate-400">
          Create a testimonial from {review.customer_name}&apos;s review.
        </p>
        <div className="mt-4 grid gap-3">
          <label className="grid gap-1 text-sm">
            Customer location <span className="text-xs text-slate-500">Optional</span>
            <input
              type="text"
              {...register("customer_location")}
              className="rounded-xl border border-white/10 bg-[#0B0B0F] p-3 outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20"
            />
            {errors.customer_location?.message && <span className="text-xs text-red-300">{errors.customer_location.message}</span>}
          </label>
          <label className="grid gap-1 text-sm">
            Display order <span className="text-xs text-slate-500">Optional</span>
            <input
              type="number"
              {...register("display_order")}
              className="rounded-xl border border-white/10 bg-[#0B0B0F] p-3 outline-none focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/20"
            />
            {errors.display_order?.message && <span className="text-xs text-red-300">{errors.display_order.message}</span>}
          </label>
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
            type="submit"
            disabled={loading}
            className="rounded-lg bg-cyan-400 px-4 py-2 text-sm font-semibold text-slate-950 focus:outline-none focus:ring-2 focus:ring-cyan-300 disabled:opacity-60"
          >
            {loading ? "Promoting..." : "Promote"}
          </button>
        </div>
      </form>
    </div>
  );
}

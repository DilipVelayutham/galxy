"use client";

import { Check, Edit, Megaphone, Trash2, X } from "lucide-react";
import type { Review } from "../../../types/review";

interface ReviewActionsProps {
  review: Review;
  loading: boolean;
  onApprove: (review: Review) => void;
  onReject: (review: Review) => void;
  onDelete: (review: Review) => void;
  onPromote: (review: Review) => void;
  onEdit: (review: Review) => void;
}

export function ReviewActions({ review, loading, onApprove, onReject, onDelete, onPromote, onEdit }: ReviewActionsProps) {
  return (
    <div className="flex flex-wrap justify-end gap-2">
      <button
        type="button"
        disabled={loading}
        onClick={() => onEdit(review)}
        aria-label={`Edit review by ${review.customer_name}`}
        className="inline-flex h-9 items-center gap-1 rounded-lg border border-white/10 bg-white/5 px-3 text-xs font-semibold text-slate-300 transition hover:bg-white/10 focus:outline-none focus:ring-2 focus:ring-slate-400 disabled:cursor-not-allowed disabled:opacity-50"
      >
        <Edit className="h-3.5 w-3.5" aria-hidden="true" /> Edit
      </button>
      {!review.is_approved && (
        <button
          type="button"
          disabled={loading}
          onClick={() => onApprove(review)}
          aria-label={`Approve review by ${review.customer_name}`}
          className="inline-flex h-9 items-center gap-1 rounded-lg border border-emerald-400/30 bg-emerald-400/10 px-3 text-xs font-semibold text-emerald-200 transition hover:bg-emerald-400/20 focus:outline-none focus:ring-2 focus:ring-emerald-400 disabled:cursor-not-allowed disabled:opacity-50"
        >
          <Check className="h-3.5 w-3.5" aria-hidden="true" /> Approve
        </button>
      )}
      <button
        type="button"
        disabled={loading}
        onClick={() => onReject(review)}
        aria-label={`Reject review by ${review.customer_name}`}
        className="inline-flex h-9 items-center gap-1 rounded-lg border border-amber-400/30 bg-amber-400/10 px-3 text-xs font-semibold text-amber-200 transition hover:bg-amber-400/20 focus:outline-none focus:ring-2 focus:ring-amber-400 disabled:cursor-not-allowed disabled:opacity-50"
      >
        <X className="h-3.5 w-3.5" aria-hidden="true" /> Reject
      </button>
      {review.is_approved && (
        <button
          type="button"
          disabled={loading}
          onClick={() => onPromote(review)}
          aria-label={`Promote review by ${review.customer_name} to testimonial`}
          className="inline-flex h-9 items-center gap-1 rounded-lg border border-cyan-400/30 bg-cyan-400/10 px-3 text-xs font-semibold text-cyan-200 transition hover:bg-cyan-400/20 focus:outline-none focus:ring-2 focus:ring-cyan-400 disabled:cursor-not-allowed disabled:opacity-50"
        >
          <Megaphone className="h-3.5 w-3.5" aria-hidden="true" /> Promote
        </button>
      )}
      <button
        type="button"
        disabled={loading}
        onClick={() => onDelete(review)}
        aria-label={`Delete review by ${review.customer_name}`}
        className="inline-flex h-9 items-center gap-1 rounded-lg border border-red-400/30 bg-red-400/10 px-3 text-xs font-semibold text-red-200 transition hover:bg-red-400/20 focus:outline-none focus:ring-2 focus:ring-red-400 disabled:cursor-not-allowed disabled:opacity-50"
      >
        <Trash2 className="h-3.5 w-3.5" aria-hidden="true" /> Delete
      </button>
    </div>
  );
}

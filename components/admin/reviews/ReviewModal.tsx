"use client";

import type { Review } from "../../../types/review";
import { ReviewForm } from "./ReviewForm";
import { useFocusTrap } from "../../../hooks/useFocusTrap";

export interface ReviewModalProps {
  open: boolean;
  review?: Review | null;
  loading: boolean;
  onClose: () => void;
  onSubmit: (values: Partial<Review>) => Promise<void>;
}

export function ReviewModal({ open, review, loading, onClose, onSubmit }: ReviewModalProps) {
  const containerRef = useFocusTrap(open, onClose);

  if (!open) return null;

  return (
    <div
      ref={containerRef}
      className="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-black/70 p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="review-modal-title"
    >
      <div className="w-full max-w-2xl rounded-2xl border border-white/10 bg-[#16161C] p-5 text-white shadow-2xl">
        <h2 id="review-modal-title" className="text-lg font-semibold">
          {review ? "Edit Review" : "Create Review"}
        </h2>
        <p className="mb-4 mt-1 text-sm text-slate-400">
          {review ? "Modify review fields and update attachments." : "Add a new product review directly."}
        </p>
        <ReviewForm review={review} loading={loading} onCancel={onClose} onSubmit={onSubmit} />
      </div>
    </div>
  );
}

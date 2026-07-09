"use client";

import { useState } from "react";
import { ChevronLeft, ChevronRight, Star, X } from "lucide-react";
import type { Review } from "../../../types/review";
import { cn } from "../../../utils/constants";
import { ReviewActions } from "./ReviewActions";
import { useFocusTrap } from "../../../hooks/useFocusTrap";

interface ReviewTableProps {
  reviews: Review[];
  loading: boolean;
  error: string | null;
  actionId: string | null;
  onApprove: (review: Review) => void;
  onReject: (review: Review) => void;
  onDelete: (review: Review) => void;
  onPromote: (review: Review) => void;
  onEdit: (review: Review) => void;
  onToggleFeatured: (review: Review) => void;
  onRetry: () => void;
}

const formatDate = (value?: string) => {
  if (!value) return "-";
  try {
    return new Intl.DateTimeFormat("en", { dateStyle: "medium" }).format(new Date(value));
  } catch {
    return "-";
  }
};

const getProductName = (review: Review) => {
  return review?.product?.name ?? review?.product?.title ?? review?.product_name ?? review?.product_id ?? "Unknown Product";
};

export function ReviewTable({
  reviews,
  loading,
  error,
  actionId,
  onApprove,
  onReject,
  onDelete,
  onPromote,
  onEdit,
  onToggleFeatured,
  onRetry,
}: ReviewTableProps) {
  const [expanded, setExpanded] = useState<Set<string>>(new Set());
  const [lightboxImages, setLightboxImages] = useState<string[] | null>(null);
  const [lightboxIndex, setLightboxIndex] = useState<number>(0);

  const lightboxOpen = Boolean(lightboxImages && lightboxImages.length > 0);
  const lightboxRef = useFocusTrap(lightboxOpen, () => setLightboxImages(null));

  const toggleExpanded = (reviewId: string) => {
    setExpanded((current) => {
      const next = new Set(current);
      if (next.has(reviewId)) next.delete(reviewId);
      else next.add(reviewId);
      return next;
    });
  };

  if (loading) {
    return (
      <div className="rounded-2xl border border-white/10 bg-[#16161C] p-4">
        <div className="space-y-4" aria-label="Loading reviews">
          <div className="h-10 rounded-xl bg-white/[0.03] animate-pulse w-full" />
          {Array.from({ length: 5 }).map((_, index) => (
            <div key={index} className="grid grid-cols-5 gap-4 items-center h-14 animate-pulse rounded-xl bg-white/5 px-4">
              <div className="h-4 bg-white/10 rounded w-3/4" />
              <div className="h-4 bg-white/10 rounded w-1/2" />
              <div className="h-4 bg-white/10 rounded w-1/4" />
              <div className="h-4 bg-white/10 rounded w-1/3" />
              <div className="h-8 bg-white/10 rounded ml-auto w-24" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-2xl border border-red-400/20 bg-[#16161C] p-6 text-center">
        <p className="text-sm text-red-200">{error}</p>
        <button
          type="button"
          onClick={onRetry}
          className="mt-4 rounded-lg bg-cyan-400 px-4 py-2 text-sm font-semibold text-slate-950 focus:outline-none focus:ring-2 focus:ring-cyan-300"
        >
          Retry
        </button>
      </div>
    );
  }

  const reviewsList = Array.isArray(reviews) ? reviews : [];

  if (reviewsList.length === 0) {
    return (
      <div className="rounded-2xl border border-white/10 bg-[#16161C] p-8 text-center text-sm text-slate-400">
        No reviews match the current filters.
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-2xl border border-white/10 bg-[#16161C] shadow-xl shadow-black/20">
      <div className="overflow-x-auto">
        <table className="min-w-[1200px] w-full border-collapse text-left text-sm">
          <thead className="bg-white/[0.03] text-xs uppercase tracking-wide text-slate-400">
            <tr>
              <th className="px-4 py-3 font-semibold">Product</th>
              <th className="px-4 py-3 font-semibold">Customer</th>
              <th className="px-4 py-3 font-semibold">Rating</th>
              <th className="px-4 py-3 font-semibold">Featured</th>
              <th className="px-4 py-3 font-semibold">Images</th>
              <th className="px-4 py-3 font-semibold">Comment</th>
              <th className="px-4 py-3 font-semibold">Order Number</th>
              <th className="px-4 py-3 font-semibold">Submitted Date</th>
              <th className="px-4 py-3 font-semibold">Status</th>
              <th className="px-4 py-3 text-right font-semibold">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/10 text-slate-200">
            {reviewsList.map((review) => {
              if (!review || !review._id) return null;
              
              const isExpanded = expanded.has(review._id);
              const commentText = review.comment ?? "";
              const isLong = commentText.length > 140;
              const status = review.status ?? (review.is_approved ? "approved" : "pending");
              const reviewImages = Array.isArray(review.images) ? review.images : [];

              return (
                <tr key={review._id} className="align-top transition hover:bg-white/[0.025]">
                  <td className="px-4 py-4 font-medium text-white">{getProductName(review)}</td>
                  <td className="px-4 py-4">
                    <div className="flex flex-wrap items-center gap-1.5">
                      <span className="font-medium text-slate-200">{review.customer_name ?? "Unknown Customer"}</span>
                      {review.order_number && (
                        <span
                          className="inline-flex items-center rounded-full bg-emerald-400/10 px-2 py-0.5 text-[10px] font-medium text-emerald-300 border border-emerald-400/20"
                          title={`Verified purchase via Order #${review.order_number}`}
                        >
                          Verified
                        </span>
                      )}
                    </div>
                    {review.email && <div className="text-xs text-slate-500 mt-0.5">{review.email}</div>}
                  </td>
                  <td className="px-4 py-4">
                    <span className="inline-flex items-center gap-1 text-amber-200">
                      <Star className="h-4 w-4 fill-amber-300 text-amber-300" aria-hidden="true" />
                      {review.rating ?? 5}
                    </span>
                  </td>
                  <td className="px-4 py-4">
                    <button
                      type="button"
                      onClick={() => onToggleFeatured(review)}
                      disabled={actionId === review._id}
                      className={cn(
                        "inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold border transition focus:outline-none focus:ring-2 focus:ring-cyan-400 disabled:opacity-60",
                        review.is_featured
                          ? "bg-cyan-400/15 text-cyan-300 border-cyan-400/30"
                          : "bg-white/5 text-slate-400 border-white/5 hover:bg-white/10 hover:text-slate-300"
                      )}
                    >
                      {review.is_featured ? "Featured" : "Standard"}
                    </button>
                  </td>
                  <td className="px-4 py-4">
                    {reviewImages.length > 0 ? (
                      <button
                        type="button"
                        onClick={() => {
                          setLightboxImages(reviewImages);
                          setLightboxIndex(0);
                        }}
                        className="flex items-center gap-2 group focus:outline-none focus:ring-2 focus:ring-cyan-400 rounded-lg p-0.5"
                        aria-label={`View ${reviewImages.length} image${reviewImages.length > 1 ? "s" : ""} for ${getProductName(review)}`}
                      >
                        <div className="relative h-10 w-10 shrink-0 overflow-hidden rounded-lg border border-white/10">
                          {/* eslint-disable-next-line @next/next/no-img-element */}
                          <img
                            src={reviewImages[0]}
                            alt={`${getProductName(review)} preview`}
                            className="h-full w-full object-cover transition duration-200 group-hover:scale-110"
                          />
                        </div>
                        {reviewImages.length > 1 && (
                          <span className="text-xs font-medium text-slate-400">+{reviewImages.length - 1}</span>
                        )}
                      </button>
                    ) : (
                      <span className="text-xs text-slate-500">No Images</span>
                    )}
                  </td>
                  <td className="max-w-[320px] px-4 py-4 text-slate-300">
                    {review.title && <h4 className="font-semibold text-white text-xs mb-1">{review.title}</h4>}
                    <p className={cn(!isExpanded && "line-clamp-2")}>{commentText}</p>
                    {isLong && (
                      <button
                        type="button"
                        onClick={() => toggleExpanded(review._id)}
                        className="mt-1 text-xs font-semibold text-cyan-300 hover:text-cyan-200 focus:outline-none focus:ring-2 focus:ring-cyan-400"
                      >
                        {isExpanded ? "Show Less" : "Read More"}
                      </button>
                    )}
                  </td>
                  <td className="px-4 py-4 text-slate-300">{review.order_number ?? "-"}</td>
                  <td className="px-4 py-4 text-slate-300">{formatDate(review.submitted_at ?? review.created_at)}</td>
                  <td className="px-4 py-4">
                    <span
                      className={cn(
                        "rounded-full px-2.5 py-1 text-xs font-semibold capitalize",
                        status === "approved"
                          ? "bg-emerald-400/10 text-emerald-200"
                          : status === "rejected"
                            ? "bg-red-400/10 text-red-200"
                            : "bg-amber-400/10 text-amber-200"
                      )}
                    >
                      {status}
                    </span>
                  </td>
                  <td className="px-4 py-4">
                    <ReviewActions
                      review={review}
                      loading={actionId === review._id}
                      onApprove={onApprove}
                      onReject={onReject}
                      onDelete={onDelete}
                      onPromote={onPromote}
                      onEdit={onEdit}
                    />
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      {lightboxImages && lightboxImages.length > 0 && (
        <div
          ref={lightboxRef}
          className="fixed inset-0 z-[100] flex items-center justify-center bg-black/90 p-4 backdrop-blur-sm animate-fade-in"
          role="dialog"
          aria-modal="true"
          aria-label="Image gallery lightbox"
        >
          <button
            type="button"
            onClick={() => setLightboxImages(null)}
            className="absolute right-4 top-4 rounded-full bg-white/10 p-2 text-white hover:bg-white/20 transition focus:outline-none focus:ring-2 focus:ring-cyan-400"
            aria-label="Close image lightbox"
          >
            <X className="h-6 w-6" />
          </button>

          {lightboxImages.length > 1 && (
            <button
              type="button"
              onClick={() => setLightboxIndex((current) => (current - 1 + lightboxImages.length) % lightboxImages.length)}
              className="absolute left-4 top-1/2 -translate-y-1/2 rounded-full bg-white/10 p-3 text-white hover:bg-white/20 transition focus:outline-none focus:ring-2 focus:ring-cyan-400"
              aria-label="Previous image"
            >
              <ChevronLeft className="h-6 w-6" />
            </button>
          )}

          <div className="max-h-[80vh] max-w-[80vw] flex flex-col items-center">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={lightboxImages[lightboxIndex]}
              alt={`Gallery image ${lightboxIndex + 1}`}
              className="max-h-[75vh] max-w-full rounded-lg object-contain shadow-2xl transition-all duration-300"
            />
            {lightboxImages.length > 1 && (
              <span className="mt-4 text-xs font-semibold text-slate-400">
                Image {lightboxIndex + 1} of {lightboxImages.length}
              </span>
            )}
          </div>

          {lightboxImages.length > 1 && (
            <button
              type="button"
              onClick={() => setLightboxIndex((current) => (current + 1) % lightboxImages.length)}
              className="absolute right-4 top-1/2 -translate-y-1/2 rounded-full bg-white/10 p-3 text-white hover:bg-white/20 transition focus:outline-none focus:ring-2 focus:ring-cyan-400"
              aria-label="Next image"
            >
              <ChevronRight className="h-6 w-6" />
            </button>
          )}
        </div>
      )}
    </div>
  );
}

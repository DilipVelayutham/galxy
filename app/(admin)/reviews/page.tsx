"use client";

import { useState } from "react";
import { Plus } from "lucide-react";
import { Toaster } from "react-hot-toast";
import { DeleteConfirmDialog } from "../../../components/admin/reviews/DeleteConfirmDialog";
import { PromoteDialog } from "../../../components/admin/reviews/PromoteDialog";
import { RejectDialog } from "../../../components/admin/reviews/RejectDialog";
import { ReviewFilters } from "../../../components/admin/reviews/ReviewFilters";
import { ReviewTable } from "../../../components/admin/reviews/ReviewTable";
import { ReviewModal } from "../../../components/admin/reviews/ReviewModal";
import { ReorderList } from "../../../components/admin/testimonials/ReorderList";
import { TestimonialModal } from "../../../components/admin/testimonials/TestimonialModal";
import { TestimonialTable } from "../../../components/admin/testimonials/TestimonialTable";
import { useReviews } from "../../../hooks/useReviews";
import { useTestimonials } from "../../../hooks/useTestimonials";
import type { Review } from "../../../types/review";
import type { Testimonial, TestimonialFormValues } from "../../../types/testimonial";
import { cn } from "../../../utils/constants";

type AdminTab = "reviews" | "testimonials";

export default function AdminReviewsPage() {
  const [activeTab, setActiveTab] = useState<AdminTab>("reviews");
  const [rejectReview, setRejectReview] = useState<Review | null>(null);
  const [deleteReview, setDeleteReview] = useState<Review | null>(null);
  const [promoteReview, setPromoteReview] = useState<Review | null>(null);
  const [testimonialModalOpen, setTestimonialModalOpen] = useState(false);
  const [editingTestimonial, setEditingTestimonial] = useState<Testimonial | null>(null);
  const [deleteTestimonial, setDeleteTestimonial] = useState<Testimonial | null>(null);
  const [testimonialSaving, setTestimonialSaving] = useState(false);

  const [reviewModalOpen, setReviewModalOpen] = useState(false);
  const [editingReview, setEditingReview] = useState<Review | null>(null);
  const [reviewSaving, setReviewSaving] = useState(false);

  const testimonials = useTestimonials();
  const reviews = useReviews(() => {
    void testimonials.fetchTestimonials();
  });

  const openCreateTestimonial = () => {
    setEditingTestimonial(null);
    setTestimonialModalOpen(true);
  };

  const handleSaveTestimonial = async (values: TestimonialFormValues) => {
    setTestimonialSaving(true);
    try {
      if (editingTestimonial) {
        await testimonials.update(editingTestimonial._id, values);
      } else {
        await testimonials.create(values);
      }
      setTestimonialModalOpen(false);
      setEditingTestimonial(null);
    } catch (error) {
      console.error("Error saving testimonial:", error);
    } finally {
      setTestimonialSaving(false);
    }
  };

  const openCreateReview = () => {
    setEditingReview(null);
    setReviewModalOpen(true);
  };

  const openEditReview = (review: Review) => {
    setEditingReview(review);
    setReviewModalOpen(true);
  };

  const handleSaveReview = async (values: Partial<Review>) => {
    setReviewSaving(true);
    try {
      if (editingReview) {
        await reviews.update(editingReview._id, values);
      } else {
        await reviews.create(values);
      }
      setReviewModalOpen(false);
      setEditingReview(null);
    } catch (error) {
      console.error("Error saving review:", error);
    } finally {
      setReviewSaving(false);
    }
  };

  return (
    <main className="min-h-screen bg-[#0B0B0F] px-4 py-6 text-white sm:px-6 lg:px-8">
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: "#16161C",
            color: "#fff",
            border: "1px solid rgba(255,255,255,0.1)",
          },
        }}
      />
      <div className="mx-auto grid max-w-7xl gap-6">
        <header className="flex flex-col gap-4 rounded-2xl border border-white/10 bg-[#16161C] p-5 shadow-xl shadow-black/20 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-300">Module 9D</p>
            <h1 className="mt-2 text-2xl font-semibold tracking-tight md:text-3xl">Admin Moderation & Testimonials</h1>
            <p className="mt-2 max-w-2xl text-sm text-slate-400">
              Moderate product reviews, promote approved customer feedback, and manage testimonial ordering.
            </p>
          </div>
          <div className="flex rounded-xl border border-white/10 bg-[#0B0B0F] p-1" role="tablist" aria-label="Admin reviews section">
            {(["reviews", "testimonials"] as const).map((tab) => (
              <button
                key={tab}
                type="button"
                role="tab"
                aria-selected={activeTab === tab}
                onClick={() => setActiveTab(tab)}
                className={cn(
                  "rounded-lg px-4 py-2 text-sm font-medium capitalize transition focus:outline-none focus:ring-2 focus:ring-cyan-400",
                  activeTab === tab ? "bg-cyan-400 text-slate-950" : "text-slate-300 hover:bg-white/5 hover:text-white"
                )}
              >
                {tab}
              </button>
            ))}
          </div>
        </header>

        {activeTab === "reviews" ? (
          <section className="grid gap-4" aria-labelledby="review-queue-title">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
              <div>
                <h2 id="review-queue-title" className="text-xl font-semibold">Review Moderation Queue</h2>
                <p className="text-sm text-slate-500">
                  Pending reviews load by default. Approvals update the queue optimistically.
                </p>
              </div>
              <div className="flex items-center gap-3">
                <button
                  type="button"
                  onClick={openCreateReview}
                  className="inline-flex items-center justify-center gap-2 rounded-xl bg-cyan-400 px-4 py-2 text-sm font-semibold text-slate-950 focus:outline-none focus:ring-2 focus:ring-cyan-300"
                >
                  <Plus className="h-4 w-4" aria-hidden="true" /> Create Review
                </button>
                <p className="text-sm text-slate-400">{reviews.total} total</p>
              </div>
            </div>
            <ReviewFilters filters={reviews.filters} onChange={reviews.updateFilters} />
            <ReviewTable
              reviews={reviews.filteredReviews}
              loading={reviews.loading}
              error={reviews.error}
              actionId={reviews.actionId}
              onApprove={(review) => void reviews.approve(review)}
              onReject={setRejectReview}
              onDelete={setDeleteReview}
              onPromote={setPromoteReview}
              onEdit={openEditReview}
              onToggleFeatured={(review) => void reviews.toggleFeatured(review)}
              onRetry={() => void reviews.fetchReviews()}
            />
            <nav className="flex items-center justify-between rounded-2xl border border-white/10 bg-[#16161C] p-3" aria-label="Review pagination">
              <button
                type="button"
                disabled={reviews.filters.page <= 1 || reviews.loading}
                onClick={() => reviews.updateFilters({ page: reviews.filters.page - 1 })}
                className="rounded-lg px-4 py-2 text-sm text-slate-300 hover:bg-white/5 focus:outline-none focus:ring-2 focus:ring-cyan-400 disabled:cursor-not-allowed disabled:opacity-40"
              >
                Previous
              </button>
              <span className="text-sm text-slate-400">
                Page {reviews.filters.page} of {reviews.totalPages}
              </span>
              <button
                type="button"
                disabled={reviews.filters.page >= reviews.totalPages || reviews.loading}
                onClick={() => reviews.updateFilters({ page: reviews.filters.page + 1 })}
                className="rounded-lg px-4 py-2 text-sm text-slate-300 hover:bg-white/5 focus:outline-none focus:ring-2 focus:ring-cyan-400 disabled:cursor-not-allowed disabled:opacity-40"
              >
                Next
              </button>
            </nav>
          </section>
        ) : (
          <section className="grid gap-4" aria-labelledby="testimonial-manager-title">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
              <div>
                <h2 id="testimonial-manager-title" className="text-xl font-semibold">Testimonial Manager</h2>
                <p className="text-sm text-slate-500">
                  Create manual testimonials, edit promoted entries, delete hard, and reorder display sequence.
                </p>
              </div>
              <button
                type="button"
                onClick={openCreateTestimonial}
                className="inline-flex items-center justify-center gap-2 rounded-xl bg-cyan-400 px-4 py-2 text-sm font-semibold text-slate-950 focus:outline-none focus:ring-2 focus:ring-cyan-300"
              >
                <Plus className="h-4 w-4" aria-hidden="true" /> Create Testimonial
              </button>
            </div>
            <TestimonialTable
              testimonials={testimonials.testimonials}
              loading={testimonials.loading}
              error={testimonials.error}
              actionId={testimonials.actionId}
              onEdit={(testimonial) => {
                setEditingTestimonial(testimonial);
                setTestimonialModalOpen(true);
              }}
              onDelete={setDeleteTestimonial}
              onRetry={() => void testimonials.fetchTestimonials()}
            />
            {!testimonials.loading && !testimonials.error && testimonials.testimonials.length > 1 && (
              <ReorderList testimonials={testimonials.testimonials} onReorder={(items) => void testimonials.reorder(items)} />
            )}
          </section>
        )}
      </div>

      <RejectDialog
        review={rejectReview}
        loading={reviews.actionId === rejectReview?._id}
        onClose={() => setRejectReview(null)}
        onConfirm={(reviewId, reason) => reviews.reject(reviewId, reason ? { reason } : {})}
      />
      <PromoteDialog
        review={promoteReview}
        loading={reviews.actionId === promoteReview?._id}
        onClose={() => setPromoteReview(null)}
        onConfirm={reviews.promote}
      />
      <DeleteConfirmDialog
        open={Boolean(deleteReview)}
        title="Delete review?"
        description="This permanently removes the review."
        loading={reviews.actionId === deleteReview?._id}
        onClose={() => setDeleteReview(null)}
        onConfirm={async () => {
          if (!deleteReview) return;
          await reviews.remove(deleteReview._id);
          setDeleteReview(null);
        }}
      />
      <TestimonialModal
        open={testimonialModalOpen}
        testimonial={editingTestimonial}
        loading={testimonialSaving}
        onClose={() => setTestimonialModalOpen(false)}
        onSubmit={handleSaveTestimonial}
      />
      <ReviewModal
        open={reviewModalOpen}
        review={editingReview}
        loading={reviewSaving}
        onClose={() => setReviewModalOpen(false)}
        onSubmit={handleSaveReview}
      />
      <DeleteConfirmDialog
        open={Boolean(deleteTestimonial)}
        title="Delete testimonial?"
        description="This permanently removes the testimonial."
        loading={testimonials.actionId === deleteTestimonial?._id}
        onClose={() => setDeleteTestimonial(null)}
        onConfirm={async () => {
          if (!deleteTestimonial) return;
          await testimonials.remove(deleteTestimonial._id);
          setDeleteTestimonial(null);
        }}
      />
    </main>
  );
}

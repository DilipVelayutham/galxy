"use client";

import React, { useState, useEffect, useCallback } from "react";
import { useAuth } from "@/context/AuthContext";
import { useToast } from "@/context/ToastContext";
import { api } from "@/lib/api";
import { useRouter } from "next/navigation";
import { Check, X, Trash, Star, ExternalLink, Award, ShieldAlert, Loader2, RefreshCw } from "lucide-react";
import { StarRating } from "@/components/reviews/StarRating";

interface Review {
  _id: string;
  customer_name: string;
  rating: number;
  comment: string;
  images: string[];
  order_number: string;
  is_approved: boolean;
  product_id: string;
  created_at: string;
}

export default function AdminReviewsPage() {
  const { user, loading: authLoading } = useAuth();
  const { showToast } = useToast();
  const router = useRouter();
  
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [filterApproved, setFilterApproved] = useState<string>("false"); // false = pending, true = approved, all = all
  const [page, setPage] = useState<number>(1);
  const [totalPages, setTotalPages] = useState<number>(1);
  
  // Modals / Input states
  const [rejectingId, setRejectingId] = useState<string | null>(null);
  const [rejectReason, setRejectReason] = useState<string>("");
  const [promotingId, setPromotingId] = useState<string | null>(null);
  const [promoLocation, setPromoLocation] = useState<string>("Chennai");
  const [promoOrder, setPromoOrder] = useState<number>(1);

  const fetchReviews = useCallback(async () => {
    setLoading(true);
    try {
      let url = `/admin/reviews?page=${page}&limit=10`;
      if (filterApproved !== "all") {
        url += `&is_approved=${filterApproved}`;
      }
      const res = await api.get(url);
      if (res.success && res.data) {
        setReviews(res.data);
        setTotalPages(res.totalPages || 1);
      } else {
        showToast(res.message || "Failed to load reviews queue", "error");
      }
    } catch (e) {
      console.error(e);
      showToast("Error connecting to admin review services", "error");
    } finally {
      setLoading(false);
    }
  }, [page, filterApproved, showToast]);

  // Route security guard
  useEffect(() => {
    if (!authLoading) {
      if (!user) {
        router.push("/login");
      } else if (user.role !== "super_admin") {
        showToast("Access Denied: Administrator role required.", "error");
        router.push("/");
      } else {
        fetchReviews();
      }
    }
  }, [user, authLoading, router, fetchReviews, showToast]);

  const handleApprove = async (id: string) => {
    try {
      const res = await api.put(`/admin/reviews/${id}/approve`);
      if (res.success) {
        showToast("Review approved and live on product details!", "success");
        fetchReviews();
      } else {
        showToast(res.message || "Failed to approve review", "error");
      }
    } catch {
      showToast("Approval command failed", "error");
    }
  };

  const handleOpenReject = (id: string) => {
    setRejectingId(id);
    setRejectReason("");
  };

  const handleRejectSubmit = async () => {
    if (!rejectingId) return;
    try {
      const res = await api.put(`/admin/reviews/${rejectingId}/reject`, { reason: rejectReason });
      if (res.success) {
        showToast("Review rejected and hidden.", "success");
        setRejectingId(null);
        fetchReviews();
      } else {
        showToast(res.message || "Failed to reject review", "error");
      }
    } catch {
      showToast("Rejection command failed", "error");
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to permanently delete this review? This action cannot be undone.")) return;
    try {
      const res = await api.delete(`/admin/reviews/${id}`);
      if (res.success) {
        showToast("Review permanently deleted.", "success");
        fetchReviews();
      } else {
        showToast(res.message || "Failed to delete review", "error");
      }
    } catch {
      showToast("Delete command failed", "error");
    }
  };

  const handleOpenPromote = (id: string) => {
    setPromotingId(id);
    setPromoLocation("Chennai");
    setPromoOrder(1);
  };

  const handlePromoteSubmit = async () => {
    if (!promotingId) return;
    try {
      const res = await api.post(`/admin/reviews/${promotingId}/promote-to-testimonial`, {
        customer_location: promoLocation,
        display_order: Number(promoOrder)
      });
      if (res.success) {
        showToast("Promoted to homepage Testimonials!", "success");
        setPromotingId(null);
        fetchReviews();
      } else {
        showToast(res.message || "Failed to promote review", "error");
      }
    } catch {
      showToast("Promotion command failed", "error");
    }
  };

  if (authLoading || !user || user.role !== "super_admin") {
    return (
      <div className="min-h-screen bg-void-black flex flex-col items-center justify-center text-text-muted text-sm gap-2">
        <Loader2 className="w-8 h-8 animate-spin text-neon-blue" />
        <span>Authenticating admin access...</span>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-void-black text-text-primary p-6 md:p-10 selection:bg-neon-pink selection:text-void-black">
      <div className="max-w-6xl mx-auto flex flex-col gap-6">
        
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-panel-charcoal pb-5">
          <div>
            <h1 className="text-2xl font-black flex items-center gap-2">
              <ShieldAlert className="w-6 h-6 text-neon-pink drop-shadow-[0_0_8px_#FF2E8A]" />
              REVIEW MODERATION
            </h1>
            <p className="text-xs text-text-muted mt-1">
              Approve custom buyer feedback or promote top reviews to homepage testimonials.
            </p>
          </div>

          {/* Filters */}
          <div className="flex items-center gap-2.5">
            <select
              value={filterApproved}
              onChange={(e) => {
                setFilterApproved(e.target.value);
                setPage(1);
              }}
              className="p-2.5 rounded bg-panel-charcoal border border-panel-charcoal/50 text-xs text-text-primary cursor-pointer focus:outline-none focus:border-neon-violet/50"
            >
              <option value="false">Pending Approval</option>
              <option value="true">Approved Reviews</option>
              <option value="all">All Reviews</option>
            </select>

            <button
              onClick={fetchReviews}
              className="p-2.5 rounded bg-panel-charcoal border border-panel-charcoal/50 hover:border-neon-blue/40 text-text-muted hover:text-text-primary cursor-pointer transition-colors"
              title="Refresh Queue"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin text-neon-blue" : ""}`} />
            </button>
          </div>
        </div>

        {/* Content Table */}
        {loading ? (
          <div className="py-20 text-center text-sm text-text-muted">Loading review queue data...</div>
        ) : reviews.length === 0 ? (
          <div className="py-16 text-center rounded-xl bg-panel-charcoal/20 border border-panel-charcoal text-text-muted flex flex-col items-center gap-2">
            <Check className="w-10 h-10 text-neon-blue drop-shadow-[0_0_8px_#18E7FF]" />
            <p className="font-bold text-sm">Review Queue Clean!</p>
            <p className="text-xs">No pending items found matching your filter selection.</p>
          </div>
        ) : (
          <div className="flex flex-col gap-4">
            {reviews.map((rev) => (
              <div
                key={rev._id}
                className={`p-5 rounded-xl border flex flex-col md:flex-row gap-5 justify-between items-start ${
                  rev.is_approved 
                    ? "border-panel-charcoal bg-panel-charcoal/20" 
                    : "border-neon-pink/20 bg-neon-pink/[0.02]"
                }`}
              >
                {/* Review Details */}
                <div className="flex-1 flex flex-col gap-3 min-w-0">
                  <div className="flex flex-wrap items-center gap-2.5">
                    <span className="font-bold text-sm text-text-primary">{rev.customer_name}</span>
                    <span className="text-[10px] bg-panel-charcoal px-2 py-0.5 rounded text-text-muted font-bold">
                      Order: {rev.order_number}
                    </span>
                    <StarRating rating={rev.rating} size={14} />
                  </div>

                  <p className="text-sm text-text-primary leading-relaxed bg-void-black/30 p-3 rounded border border-panel-charcoal/40">
                    "{rev.comment}"
                  </p>

                  {/* Thumbnail previews */}
                  {rev.images && rev.images.length > 0 && (
                    <div className="flex gap-2">
                      {rev.images.map((img, idx) => (
                        <a
                          key={idx}
                          href={img}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="w-12 h-12 rounded border border-panel-charcoal overflow-hidden block hover:border-neon-blue/40"
                        >
                          <img src={img} alt="attachment" className="w-full h-full object-cover" />
                        </a>
                      ))}
                    </div>
                  )}

                  <span className="text-[10px] text-text-muted font-bold">
                    Submitted: {new Date(rev.created_at).toLocaleString("en-IN")}
                  </span>
                </div>

                {/* Moderation Controls */}
                <div className="flex flex-row md:flex-col gap-2 w-full md:w-auto flex-shrink-0 md:items-end pt-3 md:pt-0 border-t md:border-t-0 border-panel-charcoal/50">
                  {!rev.is_approved ? (
                    <button
                      onClick={() => handleApprove(rev._id)}
                      className="flex-1 md:flex-none px-4 py-2 rounded-lg bg-neon-blue/10 text-neon-blue border border-neon-blue/30 hover:bg-neon-blue/20 text-xs font-bold transition-all cursor-pointer flex items-center justify-center gap-1.5"
                    >
                      <Check className="w-3.5 h-3.5" /> APPROVE
                    </button>
                  ) : (
                    <button
                      onClick={() => handleOpenPromote(rev._id)}
                      className="flex-1 md:flex-none px-4 py-2 rounded-lg bg-neon-violet/10 text-neon-violet border border-neon-violet/30 hover:bg-neon-violet/20 text-xs font-bold transition-all cursor-pointer flex items-center justify-center gap-1.5"
                    >
                      <Award className="w-3.5 h-3.5" /> PROMOTE TO TESTIMONIAL
                    </button>
                  )}

                  {!rev.is_approved ? (
                    <button
                      onClick={() => handleOpenReject(rev._id)}
                      className="flex-1 md:flex-none px-4 py-2 rounded-lg bg-neon-pink/10 text-neon-pink border border-neon-pink/30 hover:bg-neon-pink/20 text-xs font-bold transition-all cursor-pointer flex items-center justify-center gap-1.5"
                    >
                      <X className="w-3.5 h-3.5" /> REJECT
                    </button>
                  ) : null}

                  <button
                    onClick={() => handleDelete(rev._id)}
                    className="px-3.5 py-2 rounded-lg border border-text-muted/20 hover:border-neon-pink/50 text-text-muted hover:text-neon-pink text-xs font-bold transition-colors cursor-pointer flex items-center justify-center gap-1.5"
                  >
                    <Trash className="w-3.5 h-3.5" /> DELETE
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Reject Modal */}
      {rejectingId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-void-black/80 p-4">
          <div className="w-full max-w-md p-6 rounded-xl glass-panel border border-neon-pink/30 flex flex-col gap-4 shadow-2xl">
            <h3 className="text-base font-bold text-neon-pink flex items-center gap-2">
              Reject Submission Comment
            </h3>
            <div className="flex flex-col gap-1.5">
              <label className="text-[10px] text-text-muted uppercase font-bold tracking-wider">Reason / Feedback Notes</label>
              <textarea
                value={rejectReason}
                onChange={(e) => setRejectReason(e.target.value)}
                placeholder="Optional explanation notes for internal records..."
                rows={3}
                className="w-full p-3 rounded bg-void-black border border-panel-charcoal text-sm text-text-primary focus:outline-none focus:border-neon-pink/40"
              />
            </div>
            <div className="flex gap-3 justify-end mt-2">
              <button
                onClick={() => setRejectingId(null)}
                className="px-4 py-2 rounded bg-panel-charcoal text-xs text-text-muted font-bold hover:text-text-primary cursor-pointer"
              >
                Cancel
              </button>
              <button
                onClick={handleRejectSubmit}
                className="px-4 py-2 rounded bg-neon-pink text-void-black text-xs font-black hover:bg-neon-pink/80 cursor-pointer"
              >
                Confirm Reject
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Promote Modal */}
      {promotingId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-void-black/80 p-4">
          <div className="w-full max-w-md p-6 rounded-xl glass-panel border border-neon-violet/30 flex flex-col gap-4 shadow-2xl">
            <h3 className="text-base font-bold text-neon-violet flex items-center gap-2">
              Promote Review to Homepage Testimonial
            </h3>
            <div className="flex flex-col gap-3">
              <div className="flex flex-col gap-1">
                <label className="text-[10px] text-text-muted uppercase font-bold tracking-wider">Customer Location</label>
                <input
                  type="text"
                  value={promoLocation}
                  onChange={(e) => setPromoLocation(e.target.value)}
                  className="p-2.5 rounded bg-void-black border border-panel-charcoal text-sm text-text-primary focus:outline-none"
                  placeholder="e.g. Chennai, Bangalore"
                />
              </div>
              <div className="flex flex-col gap-1">
                <label className="text-[10px] text-text-muted uppercase font-bold tracking-wider">Display Ordering Priority</label>
                <input
                  type="number"
                  value={promoOrder}
                  onChange={(e) => setPromoOrder(Number(e.target.value))}
                  className="p-2.5 rounded bg-void-black border border-panel-charcoal text-sm text-text-primary focus:outline-none"
                  min={1}
                />
              </div>
            </div>
            <div className="flex gap-3 justify-end mt-4">
              <button
                onClick={() => setPromotingId(null)}
                className="px-4 py-2 rounded bg-panel-charcoal text-xs text-text-muted font-bold hover:text-text-primary cursor-pointer"
              >
                Cancel
              </button>
              <button
                onClick={handlePromoteSubmit}
                className="px-4 py-2 rounded bg-neon-violet text-void-black text-xs font-black hover:bg-neon-violet/80 cursor-pointer"
              >
                Create Testimonial
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

"use client";

import React, { useState, useEffect, useCallback, useRef } from "react";
import { StarRating } from "./StarRating";
import { api } from "@/lib/api";
import { ChevronLeft, ChevronRight, MessageSquare, Calendar, X, AlertTriangle, RefreshCw } from "lucide-react";

// Client-safe Review interface excluding user_id or order_id
interface Review {
  _id: string;
  customer_name: string;
  rating: number;
  comment: string;
  images: string[];
  created_at: string;
}

interface ReviewListProps {
  productId: string;
  refreshTrigger?: number;
}

const ReviewSkeleton: React.FC = () => (
  <div className="p-5 rounded-xl bg-panel-charcoal/10 border border-panel-charcoal/30 flex flex-col gap-3.5 animate-pulse">
    <div className="flex justify-between items-start gap-4">
      <div className="flex flex-col gap-2">
        <div className="h-4 w-28 bg-panel-charcoal/40 rounded" />
        <div className="h-3.5 w-16 bg-panel-charcoal/30 rounded mt-1" />
      </div>
      <div className="h-3 w-20 bg-panel-charcoal/20 rounded" />
    </div>
    <div className="space-y-2 mt-1">
      <div className="h-3.5 w-full bg-panel-charcoal/20 rounded" />
      <div className="h-3.5 w-[85%] bg-panel-charcoal/20 rounded" />
    </div>
    <div className="flex gap-2.5 mt-2">
      <div className="w-14 h-14 bg-panel-charcoal/30 rounded-lg" />
      <div className="w-14 h-14 bg-panel-charcoal/30 rounded-lg" />
    </div>
  </div>
);

export const ReviewList: React.FC<ReviewListProps> = ({ productId, refreshTrigger = 0 }) => {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [sort, setSort] = useState<string>("newest");
  const [page, setPage] = useState<number>(1);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [total, setTotal] = useState<number>(0);
  const [activeImage, setActiveImage] = useState<string | null>(null);
  const [localRefreshTrigger, setLocalRefreshTrigger] = useState<number>(0);
  
  const lightboxCloseRef = useRef<HTMLButtonElement>(null);
  const headerRef = useRef<HTMLHeadingElement>(null);

  useEffect(() => {
    const controller = new AbortController();
    
    const loadReviews = async () => {
      setLoading(true);
      setErrorMsg(null);
      try {
        const res = await api.get(
          `/products/${productId}/reviews?sort=${sort}&page=${page}&limit=5`,
          { signal: controller.signal }
        );
        if (res.success && res.data) {
          setReviews(res.data);
          setTotalPages(res.totalPages || 1);
          setTotal(res.total || 0);
        } else {
          setErrorMsg(res.message || "Failed to load reviews catalog");
        }
        setLoading(false);
      } catch (err) {
        if (err instanceof Error && err.name === "AbortError") return;
        setErrorMsg("Failed to connect to reviews service.");
        setLoading(false);
      }
    };

    loadReviews();

    return () => {
      controller.abort();
    };
  }, [productId, sort, page, refreshTrigger, localRefreshTrigger]);

  // Escape key listener for Modal close
  useEffect(() => {
    if (!activeImage) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setActiveImage(null);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    
    // Accessibility: Focus close button on mount
    setTimeout(() => {
      lightboxCloseRef.current?.focus();
    }, 50);

    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [activeImage]);

  const handlePageChange = (newPage: number) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setPage(newPage);
      headerRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  };

  const formatDate = (isoString: string) => {
    try {
      const d = new Date(isoString);
      return d.toLocaleDateString("en-IN", { year: "numeric", month: "short", day: "numeric" });
    } catch {
      return isoString;
    }
  };

  return (
    <div className="flex flex-col gap-6" aria-live="polite">
      {/* List Header & Controls */}
      <div 
        ref={headerRef}
        className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-panel-charcoal pb-4 focus:outline-none"
        tabIndex={-1}
      >
        <div>
          <h3 className="text-xl font-bold text-text-primary flex items-center gap-2">
            Reviews & Ratings <span className="text-sm font-normal text-text-muted">({total} verified reviews)</span>
          </h3>
        </div>

        {/* Sort Controls */}
        <div className="flex items-center gap-2">
          <label htmlFor="review-sort" className="text-xs text-text-muted font-bold uppercase tracking-wider">Sort</label>
          <select
            id="review-sort"
            value={sort}
            onChange={(e) => {
              setSort(e.target.value);
              setPage(1);
            }}
            className="p-2 rounded bg-panel-charcoal border border-panel-charcoal text-xs text-text-primary focus:outline-none focus:border-neon-blue/50"
          >
            <option value="newest">Newest First</option>
            <option value="highest_rated">Highest Rated</option>
            <option value="lowest_rated">Lowest Rated</option>
          </select>
        </div>
      </div>

      {/* Reviews Body */}
      {loading ? (
        <div className="flex flex-col gap-5">
          <ReviewSkeleton />
          <ReviewSkeleton />
          <ReviewSkeleton />
        </div>
      ) : errorMsg ? (
        <div className="py-12 rounded-xl border border-neon-pink/30 bg-neon-pink/5 text-center flex flex-col items-center gap-3 text-neon-pink">
          <AlertTriangle className="w-8 h-8 opacity-70 drop-shadow-[0_0_8px_#FF2E8A]" />
          <p className="text-sm font-bold">{errorMsg}</p>
          <button
            onClick={() => setLocalRefreshTrigger(prev => prev + 1)}
            className="mt-2 px-4 py-2 rounded bg-panel-charcoal hover:bg-void-black border border-neon-pink/40 hover:border-neon-pink/80 text-neon-pink text-xs font-black transition-all flex items-center gap-1.5 cursor-pointer"
          >
            <RefreshCw className="w-3.5 h-3.5" /> RETRY CONNECTION
          </button>
        </div>
      ) : reviews.length === 0 ? (
        <div className="py-12 rounded-xl border border-panel-charcoal bg-panel-charcoal/20 text-center flex flex-col items-center gap-2 text-text-muted">
          <MessageSquare className="w-8 h-8 opacity-45 text-neon-violet" />
          <p className="text-sm font-semibold">No reviews yet for this product.</p>
          <p className="text-xs">Be the first to leave feedback after purchasing!</p>
        </div>
      ) : (
        <div className="flex flex-col gap-5">
          {reviews.map((rev) => (
            <div 
              key={rev._id} 
              className="p-5 rounded-xl bg-panel-charcoal/30 border border-panel-charcoal/50 flex flex-col gap-3 hover:border-neon-blue/20 transition-all duration-300"
            >
              {/* Review Header */}
              <div className="flex justify-between items-start gap-4">
                <div>
                  <h4 className="font-bold text-text-primary text-sm">{rev.customer_name}</h4>
                  <div className="mt-1">
                    <StarRating rating={rev.rating} size={14} />
                  </div>
                </div>
                
                <div className="flex items-center gap-1.5 text-xs text-text-muted">
                  <Calendar className="w-3.5 h-3.5" aria-hidden="true" />
                  <time dateTime={rev.created_at}>{formatDate(rev.created_at)}</time>
                </div>
              </div>

              {/* Review comment text */}
              <p className="text-sm text-text-primary leading-relaxed bg-void-black/20 p-2.5 rounded border border-panel-charcoal/20">
                {rev.comment}
              </p>

              {/* Review Images */}
              {rev.images && rev.images.length > 0 && (
                <div className="flex gap-2.5 mt-1" role="group" aria-label="Review photo attachments">
                  {rev.images.map((img, idx) => (
                    <button
                      key={idx}
                      type="button"
                      onClick={() => setActiveImage(img)}
                      className="w-14 h-14 rounded-lg overflow-hidden border border-panel-charcoal hover:border-neon-blue/50 cursor-pointer transition-colors focus:outline-none focus:ring-1 focus:ring-neon-blue"
                      aria-label={`Open review image attachment number ${idx + 1}`}
                    >
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img src={img} alt="attached review detail" className="w-full h-full object-cover" />
                    </button>
                  ))}
                </div>
              )}
            </div>
          ))}

          {/* Pagination Controls */}
          {totalPages > 1 && (
            <nav className="flex items-center justify-center gap-4 mt-4" aria-label="Review Page Navigation">
              <button
                onClick={() => handlePageChange(page - 1)}
                disabled={page === 1}
                aria-label="Previous Page"
                className="p-2.5 rounded-lg bg-panel-charcoal border border-panel-charcoal/50 text-text-primary hover:border-neon-blue/40 disabled:opacity-30 disabled:pointer-events-none transition-colors cursor-pointer focus:outline-none focus:ring-1 focus:ring-neon-blue"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              
              <span className="text-xs text-text-muted font-bold" aria-current="true">
                Page {page} of {totalPages}
              </span>
              
              <button
                onClick={() => handlePageChange(page + 1)}
                disabled={page === totalPages}
                aria-label="Next Page"
                className="p-2.5 rounded-lg bg-panel-charcoal border border-panel-charcoal/50 text-text-primary hover:border-neon-blue/40 disabled:opacity-30 disabled:pointer-events-none transition-colors cursor-pointer focus:outline-none focus:ring-1 focus:ring-neon-blue"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </nav>
          )}
        </div>
      )}

      {/* Image Modal Lightbox */}
      {activeImage && (
        <div
          role="dialog"
          aria-modal="true"
          aria-label="Product review photo preview lightbox"
          className="fixed inset-0 z-50 flex items-center justify-center bg-void-black/90 p-4"
        >
          {/* Transparent click overlay to close */}
          <div 
            onClick={() => setActiveImage(null)}
            className="absolute inset-0 cursor-zoom-out" 
          />

          <div className="relative max-w-3xl max-h-[80vh] overflow-hidden rounded-xl border border-panel-charcoal bg-panel-charcoal shadow-2xl z-10">
            {/* Close Button */}
            <button
              ref={lightboxCloseRef}
              onClick={() => setActiveImage(null)}
              className="absolute top-4 right-4 z-20 p-2 rounded-full bg-void-black/70 hover:bg-void-black text-text-primary hover:text-neon-pink border border-panel-charcoal hover:border-neon-pink/40 cursor-pointer focus:outline-none focus:ring-1 focus:ring-neon-pink transition-colors"
              aria-label="Close image preview window"
            >
              <X className="w-4 h-4" />
            </button>

            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={activeImage} alt="Expanded review view attachment" className="max-w-full max-h-[75vh] object-contain" />
          </div>
        </div>
      )}
    </div>
  );
};

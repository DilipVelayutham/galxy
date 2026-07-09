"use client";

import { useEffect, useMemo, useState } from "react";
import toast from "react-hot-toast";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { getApiErrorMessage } from "../services/api";
import { reviewService } from "../services/reviewService";
import type { PromoteReviewPayload, RejectReviewPayload, Review, ReviewFiltersState } from "../types/review";
import { ADMIN_REVIEW_PAGE_SIZE } from "../utils/constants";

const initialFilters: ReviewFiltersState = {
  approval: "pending",
  product_id: "",
  search: "",
  page: 1,
  limit: ADMIN_REVIEW_PAGE_SIZE,
};

export const useReviews = (onPromoted?: () => Promise<void> | void) => {
  const queryClient = useQueryClient();
  const [filters, setFilters] = useState<ReviewFiltersState>(initialFilters);
  const [actionId, setActionId] = useState<string | null>(null);
  const [debouncedSearch, setDebouncedSearch] = useState(filters.search);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearch(filters.search);
    }, 300);

    return () => {
      clearTimeout(handler);
    };
  }, [filters.search]);

  const queryKey = [
    "reviews",
    filters.approval,
    filters.limit,
    filters.page,
    filters.product_id,
    debouncedSearch.trim(),
  ];

  const { data, isLoading, error, refetch } = useQuery({
    queryKey,
    queryFn: async () => {
      return await reviewService.list({
        page: filters.page,
        limit: filters.limit,
        product_id: filters.product_id || undefined,
        is_approved: filters.approval === "approved",
        search: debouncedSearch.trim() || undefined,
      });
    },
    retry: 1,
    staleTime: 30000,
  });

  const reviews = data?.reviews ?? [];

  const filteredReviews = useMemo(() => {
    const search = filters.search.trim().toLowerCase();
    if (!search) return reviews;

    return reviews.filter((review) => {
      const productName = review.product?.name ?? review.product?.title ?? review.product_name ?? "";
      return [
        productName,
        review.customer_name,
        review.email ?? "",
        review.title ?? "",
        review.comment,
        review.order_number ?? "",
      ]
        .join(" ")
        .toLowerCase()
        .includes(search);
    });
  }, [filters.search, reviews]);

  const updateFilters = (nextFilters: Partial<ReviewFiltersState>) => {
    setFilters((current) => ({
      ...current,
      ...nextFilters,
      page: nextFilters.page ?? 1,
    }));
  };

  const create = async (payload: Partial<Review>) => {
    setActionId("create");
    try {
      await reviewService.create(payload);
      toast.success("Review created.");
      await queryClient.invalidateQueries({ queryKey: ["reviews"] });
    } catch (err) {
      toast.error(getApiErrorMessage(err));
      throw err;
    } finally {
      setActionId(null);
    }
  };

  const update = async (reviewId: string, payload: Partial<Review>) => {
    setActionId(reviewId);
    try {
      await reviewService.update(reviewId, payload);
      toast.success("Review updated.");
      await queryClient.invalidateQueries({ queryKey: ["reviews"] });
    } catch (err) {
      toast.error(getApiErrorMessage(err));
      throw err;
    } finally {
      setActionId(null);
    }
  };

  const toggleFeatured = async (review: Review) => {
    setActionId(review._id);
    const previousData = queryClient.getQueryData(queryKey);

    if (previousData) {
      queryClient.setQueryData(queryKey, (old: any) => {
        if (!old) return old;
        return {
          ...old,
          reviews: old.reviews.map((item: Review) =>
            item._id === review._id ? { ...item, is_featured: !item.is_featured } : item
          ),
        };
      });
    }

    try {
      await reviewService.update(review._id, { is_featured: !review.is_featured });
      toast.success(review.is_featured ? "Review removed from featured." : "Review marked as featured.");
      await queryClient.invalidateQueries({ queryKey: ["reviews"] });
    } catch (err) {
      if (previousData) {
        queryClient.setQueryData(queryKey, previousData);
      }
      toast.error(getApiErrorMessage(err));
    } finally {
      setActionId(null);
    }
  };

  const approve = async (review: Review) => {
    setActionId(review._id);
    const previousData = queryClient.getQueryData(queryKey);

    if (filters.approval === "pending" && previousData) {
      queryClient.setQueryData(queryKey, (old: any) => {
        if (!old) return old;
        return {
          ...old,
          reviews: old.reviews.filter((item: Review) => item._id !== review._id),
          total: Math.max(0, old.total - 1),
        };
      });
    }

    try {
      await reviewService.approve(review._id);
      toast.success("Review approved.");
      await queryClient.invalidateQueries({ queryKey: ["reviews"] });
    } catch (err) {
      if (previousData) {
        queryClient.setQueryData(queryKey, previousData);
      }
      toast.error(getApiErrorMessage(err));
    } finally {
      setActionId(null);
    }
  };

  const reject = async (reviewId: string, payload: RejectReviewPayload) => {
    setActionId(reviewId);
    try {
      await reviewService.reject(reviewId, payload);
      toast.success("Review rejected.");
      await queryClient.invalidateQueries({ queryKey: ["reviews"] });
    } catch (err) {
      toast.error(getApiErrorMessage(err));
      throw err;
    } finally {
      setActionId(null);
    }
  };

  const remove = async (reviewId: string) => {
    setActionId(reviewId);
    try {
      await reviewService.delete(reviewId);
      toast.success("Review deleted.");
      await queryClient.invalidateQueries({ queryKey: ["reviews"] });
    } catch (err) {
      toast.error(getApiErrorMessage(err));
      throw err;
    } finally {
      setActionId(null);
    }
  };

  const promote = async (reviewId: string, payload: PromoteReviewPayload) => {
    setActionId(reviewId);
    try {
      await reviewService.promote(reviewId, payload);
      toast.success("Review promoted to testimonial.");
      await queryClient.invalidateQueries({ queryKey: ["reviews"] });
      await onPromoted?.();
    } catch (err) {
      toast.error(getApiErrorMessage(err));
      throw err;
    } finally {
      setActionId(null);
    }
  };

  return {
    actionId,
    approve,
    create,
    update,
    toggleFeatured,
    error: error ? getApiErrorMessage(error) : null,
    fetchReviews: refetch,
    filteredReviews,
    filters,
    loading: isLoading,
    promote,
    reject,
    remove,
    total: data?.total ?? 0,
    totalPages: data?.total_pages ?? 1,
    updateFilters,
  };
};

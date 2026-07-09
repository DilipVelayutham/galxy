import { api, unwrapApiResponse } from "./api";
import type {
  ApiResponse,
  PromoteReviewPayload,
  RejectReviewPayload,
  Review,
  ReviewListResult,
  ReviewQueryParams,
} from "../types/review";

const normalizeReview = (review: any): Review => {
  return {
    _id: review._id || review.id || "",
    product_id: review.product_id || "",
    product: review.product
      ? {
          _id: review.product._id || review.product.id || "",
          name: review.product.name || review.product.title || "",
          title: review.product.title,
          sku: review.product.sku,
        }
      : null,
    product_name: review.product_name,
    customer_name: review.customer_name || "",
    email: review.email,
    title: review.title,
    rating: Number(review.rating) || 5,
    comment: review.comment || "",
    order_number: review.order_number,
    is_approved: !!review.is_approved,
    is_featured: !!review.is_featured,
    images: Array.isArray(review.images) ? review.images : [],
    status: review.status,
    created_at: review.created_at || new Date().toISOString(),
    submitted_at: review.submitted_at,
  };
};

const normalizeReviewList = (payload: any, fallbackPage = 1, fallbackLimit = 10): ReviewListResult => {
  if (Array.isArray(payload)) {
    return {
      reviews: payload.map(normalizeReview),
      total: payload.length,
      page: fallbackPage,
      limit: fallbackLimit,
      total_pages: 1,
    };
  }

  const reviews = Array.isArray(payload?.reviews) ? payload.reviews : [];
  const total = typeof payload?.total === "number" ? payload.total : reviews.length;
  const page = typeof payload?.page === "number" ? payload.page : fallbackPage;
  const limit = typeof payload?.limit === "number" ? payload.limit : fallbackLimit;
  const total_pages = typeof payload?.total_pages === "number" ? payload.total_pages : typeof payload?.totalPages === "number" ? payload.totalPages : Math.max(1, Math.ceil(total / limit));

  return {
    reviews: reviews.map(normalizeReview),
    total,
    page,
    limit,
    total_pages,
  };
};

export const reviewService = {
  async list(params: ReviewQueryParams): Promise<ReviewListResult> {
    const response = await api.get<ApiResponse<unknown>>("/api/admin/reviews", { params });
    return normalizeReviewList(unwrapApiResponse(response.data), params.page, params.limit);
  },

  async create(payload: Partial<Review>): Promise<Review> {
    const response = await api.post<ApiResponse<unknown>>("/api/admin/reviews", payload);
    return normalizeReview(unwrapApiResponse(response.data));
  },

  async update(reviewId: string, payload: Partial<Review>): Promise<Review> {
    const response = await api.put<ApiResponse<unknown>>(`/api/admin/reviews/${reviewId}`, payload);
    return normalizeReview(unwrapApiResponse(response.data));
  },

  async approve(reviewId: string): Promise<Review> {
    const response = await api.put<ApiResponse<unknown>>(`/api/admin/reviews/${reviewId}/approve`);
    return normalizeReview(unwrapApiResponse(response.data));
  },

  async reject(reviewId: string, payload: RejectReviewPayload): Promise<Review> {
    const response = await api.put<ApiResponse<unknown>>(`/api/admin/reviews/${reviewId}/reject`, payload);
    return normalizeReview(unwrapApiResponse(response.data));
  },

  async delete(reviewId: string): Promise<void> {
    const response = await api.delete<ApiResponse<null>>(`/api/admin/reviews/${reviewId}`);
    unwrapApiResponse(response.data);
  },

  async promote(reviewId: string, payload: PromoteReviewPayload): Promise<void> {
    const response = await api.post<ApiResponse<unknown>>(`/api/admin/reviews/${reviewId}/promote-to-testimonial`, payload);
    unwrapApiResponse(response.data);
  },
};

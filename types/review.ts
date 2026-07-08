export type ReviewApprovalFilter = "pending" | "approved";

export interface ApiResponse<T> {
  success: boolean;
  message: string;
  data: T;
}

export interface PaginatedData<T> {
  items?: T[];
  reviews?: T[];
  testimonials?: T[];
  data?: T[];
  total?: number;
  page?: number;
  limit?: number;
  total_pages?: number;
  totalPages?: number;
}

export interface ProductSummary {
  _id: string;
  name: string;
  title?: string | undefined;
  sku?: string | undefined;
}

export interface Review {
  _id: string;
  product_id: string;
  product?: ProductSummary | null | undefined;
  product_name?: string | undefined;
  customer_name: string;
  email?: string | undefined;
  title?: string | undefined;
  rating: number;
  comment: string;
  order_number?: string | null | undefined;
  is_approved: boolean;
  is_featured: boolean;
  images: string[];
  status?: "pending" | "approved" | "rejected" | string | undefined;
  created_at: string;
  submitted_at?: string | undefined;
}

export interface ReviewFiltersState {
  approval: ReviewApprovalFilter;
  product_id: string;
  search: string;
  page: number;
  limit: number;
}

export interface ReviewListResult {
  reviews: Review[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface ReviewQueryParams {
  page?: number | undefined;
  limit?: number | undefined;
  product_id?: string | undefined;
  is_approved?: boolean | undefined;
  search?: string | undefined;
}

export interface RejectReviewPayload {
  reason?: string | undefined;
}

export interface PromoteReviewPayload {
  customer_location?: string | undefined;
  display_order?: number | undefined;
}

export interface ReviewFormValues {
  product_id: string;
  product_name?: string | undefined;
  customer_name: string;
  email?: string | undefined;
  title?: string | undefined;
  rating: number;
  comment: string;
  order_number?: string | undefined;
  is_featured: boolean;
  images: string[];
}

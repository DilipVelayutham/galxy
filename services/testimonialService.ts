import { api, unwrapApiResponse } from "./api";
import type { ApiResponse, PaginatedData } from "../types/review";
import type {
  ReorderTestimonialPayload,
  Testimonial,
  TestimonialFormValues,
  TestimonialListResult,
} from "../types/testimonial";

const normalizeTestimonials = (payload: any): TestimonialListResult => {
  const rawTestimonials: any[] = Array.isArray(payload)
    ? payload
    : Array.isArray(payload?.testimonials)
      ? payload.testimonials
      : [];

  const testimonials: Testimonial[] = rawTestimonials.map((t: any) => ({
    _id: t._id || t.id || "",
    customer_name: t.customer_name || "",
    customer_location: t.customer_location,
    quote: t.quote || "",
    rating: Number(t.rating) || 5,
    image_url: t.image_url,
    source: t.source || "manual",
    display_order: Number(t.display_order) || 0,
    is_active: t.is_active !== false,
    created_at: t.created_at,
    updated_at: t.updated_at,
  }));

  return {
    testimonials: [...testimonials].sort((a, b) => a.display_order - b.display_order),
    total: typeof payload?.total === "number" ? payload.total : testimonials.length,
  };
};

export const testimonialService = {
  async list(): Promise<TestimonialListResult> {
    const response = await api.get<ApiResponse<Testimonial[] | PaginatedData<Testimonial>>>("/api/admin/testimonials");
    return normalizeTestimonials(unwrapApiResponse(response.data));
  },

  async create(payload: TestimonialFormValues): Promise<Testimonial> {
    const response = await api.post<ApiResponse<Testimonial>>("/api/admin/testimonials", payload);
    return unwrapApiResponse(response.data);
  },

  async update(testimonialId: string, payload: TestimonialFormValues): Promise<Testimonial> {
    const response = await api.put<ApiResponse<Testimonial>>(`/api/admin/testimonials/${testimonialId}`, payload);
    return unwrapApiResponse(response.data);
  },

  async delete(testimonialId: string): Promise<void> {
    const response = await api.delete<ApiResponse<null>>(`/api/admin/testimonials/${testimonialId}`);
    unwrapApiResponse(response.data);
  },

  async reorder(payload: ReorderTestimonialPayload[]): Promise<void> {
    const response = await api.put<ApiResponse<unknown>>("/api/admin/testimonials/reorder", payload);
    unwrapApiResponse(response.data);
  },
};

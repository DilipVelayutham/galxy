export type TestimonialSource = "review" | "manual";

export interface Testimonial {
  _id: string;
  customer_name: string;
  customer_location?: string | null | undefined;
  quote: string;
  rating: number;
  image_url?: string | null | undefined;
  source: TestimonialSource;
  display_order: number;
  is_active?: boolean | undefined;
  created_at?: string | undefined;
  updated_at?: string | undefined;
}

export interface TestimonialFormValues {
  customer_name: string;
  customer_location?: string | undefined;
  quote: string;
  rating: number;
  image_url?: string | undefined;
  is_active?: boolean | undefined;
}

export interface TestimonialListResult {
  testimonials: Testimonial[];
  total: number;
}

export interface ReorderTestimonialPayload {
  testimonial_id: string;
  display_order: number;
}

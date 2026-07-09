import { z } from "zod";

export const reviewSchema = z.object({
  customer_name: z
    .string()
    .min(2, { message: "Customer name must be at least 2 characters." })
    .trim(),
  email: z
    .string()
    .trim()
    .email({ message: "Invalid email address." })
    .or(z.literal(""))
    .optional(),
  product_id: z
    .string()
    .min(1, { message: "Product ID is required." })
    .trim(),
  product_name: z.string().trim().optional().nullable(),
  title: z.string().trim().optional().nullable(),
  rating: z.coerce
    .number()
    .min(1, { message: "Rating must be at least 1." })
    .max(5, { message: "Rating cannot exceed 5." }),
  comment: z
    .string()
    .min(8, { message: "Comment must be at least 8 characters." })
    .trim(),
  order_number: z.string().trim().optional().nullable(),
  is_featured: z.boolean().default(false),
  images: z.array(z.string()).default([]),
});

export const testimonialSchema = z.object({
  customer_name: z
    .string()
    .min(2, { message: "Customer name must be at least 2 characters." })
    .trim(),
  customer_location: z.string().trim().optional().nullable(),
  quote: z
    .string()
    .min(8, { message: "Quote must be at least 8 characters." })
    .trim(),
  rating: z.coerce
    .number()
    .min(1, { message: "Rating must be at least 1." })
    .max(5, { message: "Rating cannot exceed 5." }),
  image_url: z.string().trim().optional().nullable(),
  is_active: z.boolean().default(true),
});

export const promoteSchema = z.object({
  customer_location: z.string().trim().optional().nullable(),
  display_order: z.preprocess(
    (val) => (val === "" || val === undefined || val === null ? undefined : Number(val)),
    z.number().int().min(1, { message: "Display order must be 1 or higher." }).optional()
  ),
});

export const rejectSchema = z.object({
  reason: z.string().trim().optional().nullable(),
});

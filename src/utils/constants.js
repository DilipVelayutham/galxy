/**
 * Application-wide constants for GALXY Admin Dashboard
 */

// NOTE: Categories are NOT a hard-coded list. GALXY categories are real
// documents (with their own attribute_schema, accent_color, hero_image)
// fetched from GET /api/admin/categories. See services/api/adminProductApi.js
// (getCategories) and hooks/useCategories.js. Do not reintroduce a static
// category list here -- it was the root cause of the category_id mismatch
// flagged in the compliance review.

// Product "type" enum -- must match the enum the public-facing module builds
// its gallery/configurator logic around. GALXY only has these two values.
export const PRODUCT_TYPES = [
  { value: 'pre_designed', label: 'Pre-Designed' },
  { value: 'fully_custom', label: 'Fully Custom' },
];

// Stock status options
export const STOCK_STATUS_OPTIONS = [
  { value: 'in_stock', label: 'In Stock', color: '#22C55E' },
  { value: 'made_to_order', label: 'Made to Order', color: '#F59E0B' },
  { value: 'out_of_stock', label: 'Out of Stock', color: '#EF4444' },
];

// Attribute input types supported by a category's attribute_schema.
// Drives how default_attributes fields render in ProductForm.
export const ATTRIBUTE_INPUT_TYPES = {
  TEXT: 'text',
  SELECT: 'select',
  SLIDER: 'slider',
  NUMBER: 'number',
};

// Pagination defaults
export const PAGINATION = {
  DEFAULT_PAGE: 1,
  DEFAULT_LIMIT: 10,
  PAGE_SIZE_OPTIONS: [5, 10, 20, 50],
};

// API Base URL
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api';

// Image upload constraints
export const IMAGE_UPLOAD = {
  MAX_FILE_SIZE: 5 * 1024 * 1024, // 5MB
  MAX_FILES: 8,
  ACCEPTED_TYPES: ['image/jpeg', 'image/png', 'image/webp', 'image/gif'],
};

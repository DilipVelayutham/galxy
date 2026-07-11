// types/category.ts
export interface AttributeOption {
  value: string;
  label: string;
  price_delta?: number;
  preview_image?: string;
}

export type AttributeType =
  | 'select'
  | 'color_swatch'
  | 'image_swatch'
  | 'toggle'
  | 'slider'
  | 'text_input'
  | 'number';

export interface AttributeSchemaItem {
  key: string;
  label: string;
  type: AttributeType;
  options?: AttributeOption[]; // for select, color_swatch, image_swatch
  min?: number; // for slider/number
  max?: number;
  step?: number;
  affects_ai_preview: boolean;
  required: boolean;
  display_order: number;
}

export interface SEOFields {
  meta_title?: string;
  meta_description?: string;
  og_image?: string;
}

export interface Category {
  _id: string;
  slug: string;
  name: string;
  description?: string;
  tagline?: string;
  cover_image?: string;
  banner_image?: string;
  accent_color: '#FF2E8A' | '#18E7FF' | '#9B5CFF' | '#FFD84D';
  display_order: number;
  is_active: boolean;
  attribute_schema: AttributeSchemaItem[];
  ai_prompt_template?: string;
  seo?: SEOFields;
  created_at?: string;
  updated_at?: string;
}

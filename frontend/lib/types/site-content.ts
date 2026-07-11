export interface HeroContent {
  headline: string;
  subheadline: string;
  background_video_url: string | null;
  background_image_url: string;
  cta_text: string;
  cta_link: string;
}

export interface AboutContent {
  title: string;
  body_text: string;
  images: string[];
  founder_name: string;
  founder_photo: string | null;
}

export interface FooterContent {
  tagline: string;
  quick_links: { label: string; url: string }[];
  business_hours: string;
}

export interface ContactContent {
  phone: string;
  whatsapp_number: string;
  email: string;
  address: string;
  map_embed_url: string | null;
}

export interface SeoHomeContent {
  meta_title: string;
  meta_description: string;
  og_image: string | null;
}

export interface SocialLinksContent {
  instagram: string;
  facebook: string | null;
  youtube: string | null;
}

export interface BulkSiteContent {
  hero?: HeroContent;
  about?: AboutContent;
  footer?: FooterContent;
  contact?: ContactContent;
  seo_home?: SeoHomeContent;
  social_links?: SocialLinksContent;
}

export type SectionName =
  | 'hero'
  | 'about'
  | 'footer'
  | 'contact'
  | 'seo_home'
  | 'social_links';

export type SectionContent =
  | HeroContent
  | AboutContent
  | FooterContent
  | ContactContent
  | SeoHomeContent
  | SocialLinksContent;

export interface SiteContentResponse<T extends SectionContent> {
  success: boolean;
  data: {
    section: SectionName;
    content: T;
  };
}

export interface SiteContentErrorResponse {
  success: false;
  message: string;
  errors: Record<string, string>;
}

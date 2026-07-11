"use client";

import { useEffect, useState, use, useCallback } from "react";
import Link from "next/link";
import { ArrowLeft, Sparkles, Loader2, Info, AlertTriangle } from "lucide-react";
import AttributeRenderer, { Attribute, AttributeValue } from "@/components/configurator/AttributeRenderer";

/**
 * PLACEHOLDER_BASE_PRICE
 * ---------------------
 * This is a dummy value used only for the attribute-renderer price preview on
 * this category detail page. It does NOT come from any real product record.
 *
 * Once the pricing / configurator flow moves to the Product Detail Page
 * (Module 3/4), replace this constant with the actual product's `base_price`
 * fetched from the backend.
 */
const PLACEHOLDER_BASE_PRICE = 1499;

interface CategoryDetail {
  slug: string;
  name: string;
  short_tagline: string;
  description: string;
  cover_image: string;
  banner_image: string;
  accent_color: string;
  display_order: number;
  attribute_schema: Attribute[];
}

export default function CategoryDetailPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = use(params);

  const [category, setCategory] = useState<CategoryDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [configuration, setConfiguration] = useState<Record<string, AttributeValue>>({});
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  // Auto-dismiss toast after 4 seconds
  const showToast = useCallback((msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 4000);
  }, []);
 
  useEffect(() => {
    const fetchCategory = async () => {
      await Promise.resolve();
      setLoading(true);
      setError(null);
      try {
        const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000";
        const res = await fetch(`${baseUrl}/api/categories/${slug}`);
        if (res.status === 404) {
          setError("Category not found");
          return;
        }
        if (!res.ok) {
          throw new Error(`Failed to load category details (Status ${res.status})`);
        }
        const json = await res.json();
        if (json.success && json.data) {
          const catData = json.data;
          setCategory(catData);
 
          // Initialize default configurations for attributes
          const initialConfig: Record<string, AttributeValue> = {};
          if (Array.isArray(catData.attribute_schema)) {
            catData.attribute_schema.forEach((attr: Attribute) => {
              if (attr.type === "toggle") {
                initialConfig[attr.key] = false;
              } else if (attr.type === "slider") {
                initialConfig[attr.key] = attr.min ?? 0;
              } else if (attr.options && attr.options.length > 0) {
                initialConfig[attr.key] = attr.options[0].value;
              } else {
                initialConfig[attr.key] = "";
              }
            });
          }
          setConfiguration(initialConfig);
        } else {
          throw new Error(json.message || "Invalid response format from API");
        }
      } catch (err: unknown) {
        console.error("Fetch category error:", err);
        const errorMessage = err instanceof Error ? err.message : "Something went wrong while loading category details.";
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    };
 
    fetchCategory();
  }, [slug]);
 
  const handleConfigChange = (key: string, value: AttributeValue) => {
    setConfiguration((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  /**
   * TODO — SCOPE CONFLICT (flag for Project Head review before Day 4 integration)
   * -------------------------------------------------------------------------
   * `calculateTotalPrice()` and the "Finalize & Save Design" button below are
   * OUT OF SCOPE for this Member 4 execution document (Module 2 — Public
   * Category Frontend). The broader Project Plan and Frontend Detail docs
   * assign the configurator + live pricing + "add to cart" flow to the
   * Product Detail Page owned by Module 3/4.
   *
   * This code is intentionally kept in place so it can be migrated rather than
   * rebuilt, but it should NOT be treated as finished checkout functionality.
   * The Project Head must decide before Day 4 integration whether to:
   *   (a) move this block wholesale to the product detail page, or
   *   (b) keep a read-only price preview here and handle submission in Module 3/4.
   */

  // Calculate dynamic price add-ons based on configuration
  // NOTE: Uses PLACEHOLDER_BASE_PRICE — must be replaced with a real product's
  // base_price once this logic moves to the product page (see TODO above).
  const calculateTotalPrice = () => {
    let price = PLACEHOLDER_BASE_PRICE;
    if (!category || !category.attribute_schema) return price;

    category.attribute_schema.forEach((attr) => {
      const selectedVal = configuration[attr.key];
      if (attr.options) {
        const matchingOpt = attr.options.find((opt) => opt.value === selectedVal);
        if (matchingOpt && matchingOpt.price_delta) {
          price += matchingOpt.price_delta;
        }
      }
    });
    return price;
  };

  // Helper: check if all required configuration options are populated
  const isConfigurationComplete = () => {
    if (!category || !category.attribute_schema) return false;
    return category.attribute_schema.every((attr) => {
      if (!attr.required) return true;
      const value = configuration[attr.key];
      return value !== undefined && value !== null && value !== "";
    });
  };

  if (loading) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center py-40">
        <Loader2 className="w-12 h-12 text-purple-500 animate-spin mb-4" />
        <p className="text-gray-400 text-sm font-medium animate-pulse">
          Loading custom attributes and options...
        </p>
      </div>
    );
  }

  if (error || !category) {
    return (
      <div className="flex-1 max-w-md mx-auto px-4 flex flex-col items-center justify-center text-center py-20">
        <AlertTriangle className="w-16 h-16 text-yellow-500 mb-6 drop-shadow-[0_0_15px_rgba(234,179,8,0.2)]" />
        <h2 className="text-2xl font-bold text-white mb-2">
          {error === "Category not found" ? "Category Not Found" : "Connection Lost"}
        </h2>
        <p className="text-gray-400 text-sm mb-8 leading-relaxed">
          {error === "Category not found"
            ? "The category you are looking for does not exist or has been disabled by the admin."
            : "We couldn't reach the database server. Make sure the backend service is running."}
        </p>
        <Link
          href="/categories"
          className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20 text-white font-semibold text-sm transition-all duration-200"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Categories
        </Link>
      </div>
    );
  }

  // Accent color setup
  const themeClass = `accent-${category.accent_color || "neon_pink"}`;

  return (
    <div className={`flex-1 w-full max-w-7xl mx-auto px-4 py-8 md:py-12 ${themeClass}`}>
      {/* Back Button and Navigation path */}
      <div className="flex items-center justify-between mb-8">
        <Link
          href="/categories"
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 border border-white/5 hover:border-white/10 text-gray-300 hover:text-white text-sm font-semibold transition-all duration-200"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Categories
        </Link>
        <div className="text-xs text-gray-500 font-medium">
          Categories &gt; <span className="text-gray-300 font-bold">{category.name}</span>
        </div>
      </div>

      {/* Main Grid: Responsive 2-column on desktop/tablet, 1-column on mobile */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 md:gap-12 items-start">
        
        {/* Left Column: Media & Product Details (Sticky on large screens) */}
        <div className="lg:col-span-5 lg:sticky lg:top-8 flex flex-col gap-6">
          {/* Banner / Media Card */}
          <div className="relative aspect-[4/3] rounded-2xl overflow-hidden glass-panel border border-white/5 shadow-2xl">
            {/* Ambient Background Glow matching the active accent color */}
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,var(--accent-glow),transparent_70%)] pointer-events-none" />

            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={category.banner_image || category.cover_image}
              alt={category.name}
              className="w-full h-full object-cover relative z-10"
            />
            
            {/* Floating configuration info tag */}
            <div className="absolute top-4 right-4 z-20 px-3 py-1 rounded-full bg-slate-950/80 backdrop-filter backdrop-blur-md border border-white/10 text-[10px] font-bold text-gray-300 flex items-center gap-1.5 shadow-lg">
              <Sparkles className="w-3 h-3 text-[var(--accent-text)]" />
              Dynamic Schema Rendering
            </div>

            <div className="absolute inset-0 bg-gradient-to-t from-slate-950/90 via-transparent to-transparent z-10" />
            
            <div className="absolute bottom-6 left-6 right-6 z-20">
              <h1 className="text-2xl md:text-3xl font-extrabold text-white mb-1.5 glow-text">
                {category.name}
              </h1>
              <p className="text-sm font-semibold text-[var(--accent-text)] uppercase tracking-wider">
                {category.short_tagline}
              </p>
            </div>
          </div>

          {/* Description Card */}
          <div className="p-6 rounded-2xl glass-panel border border-white/5">
            <h3 className="text-sm font-bold text-gray-300 uppercase tracking-wider mb-3">About Category</h3>
            <p className="text-gray-400 text-sm leading-relaxed">{category.description}</p>
            
            <div className="mt-5 pt-4 border-t border-white/5 flex items-center gap-3">
              <div className="w-9 h-9 rounded-lg bg-white/5 flex items-center justify-center shrink-0">
                <Info className="w-4 h-4 text-purple-400" />
              </div>
              <p className="text-xs text-gray-500 leading-normal">
                Configure choices on the right. Pricing adjust additions are shown with respective selections.
              </p>
            </div>
          </div>
        </div>

        {/* Right Column: Schema Customizer Form */}
        <div className="lg:col-span-7 flex flex-col gap-6">
          <div className="p-6 md:p-8 rounded-2xl glass-panel border border-white/5 shadow-xl relative overflow-hidden">
            {/* Header border accent */}
            <div className="absolute top-0 inset-x-0 h-[2.5px] bg-gradient-to-r from-transparent via-[var(--accent)] to-transparent" />

            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
              <div>
                <h2 className="text-xl font-bold text-white">Configure Your Creation</h2>
                <p className="text-xs text-gray-400 mt-1">Fields marked with (*) are required.</p>
              </div>
              
              {/* Dynamic Live Price Engine */}
              <div className="px-4 py-2.5 rounded-xl bg-slate-950/60 border border-white/5 flex items-center justify-between sm:justify-start gap-4">
                <span className="text-xs text-gray-500 font-bold uppercase">Est. Price</span>
                <span className={`text-xl font-extrabold ${getTextColorClass()}`}>
                  ₹{calculateTotalPrice().toLocaleString("en-IN")}
                </span>
              </div>
            </div>

            {/* Dynamic Attribute Renderer Fields */}
            {Array.isArray(category.attribute_schema) && category.attribute_schema.length > 0 ? (
              <div className="flex flex-col gap-6 md:gap-7">
                {category.attribute_schema.map((attr) => (
                  <AttributeRenderer
                    key={attr.key}
                    attribute={attr}
                    value={configuration[attr.key]}
                    onChange={handleConfigChange}
                    accentColor={category.accent_color}
                  />
                ))}
              </div>
            ) : (
              <div className="text-center py-8 border border-dashed border-white/10 rounded-xl">
                <p className="text-gray-500 text-sm">No configurable attributes found for this category.</p>
              </div>
            )}

            {/* Configurator Submission / Add to Cart CTA
                TODO: This button is a placeholder — see scope-conflict TODO above.
                Full cart integration is owned by Module 6. */}
            <div className="mt-10 pt-6 border-t border-white/5 flex flex-col sm:flex-row items-center gap-4">
              <button
                type="button"
                disabled={!isConfigurationComplete()}
                onClick={() => {
                  // Log configuration for debugging; do NOT treat as a real checkout.
                  console.log(
                    "[GALXY Placeholder] Configuration preview (not a real order):",
                    {
                      category: category.name,
                      estimatedPrice: calculateTotalPrice(),
                      configuration,
                    }
                  );
                  showToast("Coming soon — pending Module 6 cart integration");
                }}
                className={`w-full sm:w-auto flex-1 inline-flex justify-center items-center gap-2 px-6 py-4 rounded-xl font-bold text-sm transition-all duration-300 cursor-pointer ${
                  isConfigurationComplete()
                    ? category.accent_color === "neon_pink"
                      ? "bg-[#ff007f] text-slate-950 hover:bg-[#ff007f]/90 shadow-[0_0_20px_rgba(255,0,127,0.3)]"
                      : category.accent_color === "neon_blue"
                      ? "bg-[#00f0ff] text-slate-950 hover:bg-[#00f0ff]/90 shadow-[0_0_20px_rgba(0,240,255,0.3)]"
                      : category.accent_color === "neon_violet"
                      ? "bg-[#a855f7] text-white hover:bg-[#a855f7]/90 shadow-[0_0_20px_rgba(168,85,247,0.3)]"
                      : "bg-[#eab308] text-slate-950 hover:bg-[#eab308]/90 shadow-[0_0_20px_rgba(234,179,8,0.3)]"
                    : "bg-white/5 text-gray-500 border border-white/5 cursor-not-allowed"
                }`}
              >
                <Sparkles className="w-4 h-4" />
                {isConfigurationComplete() ? "Preview Configuration" : "Complete Configuration"}
              </button>
            </div>
          </div>
        </div>

      </div>

      {/* Inline toast notification */}
      {toastMessage && (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 px-6 py-3 rounded-xl glass-panel border border-white/10 shadow-2xl text-sm font-semibold text-gray-200 animate-bounce-in">
          {toastMessage}
        </div>
      )}
    </div>
  );
}

// Utility accent color class lookup to avoid typescript compiler check issues
function getTextColorClass() {
  return "glow-text text-white";
}

"use client";

import React, { useState, useEffect, use } from "react";
import { api } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { useToast } from "@/context/ToastContext";
import { AttributeRenderer, AttributeField } from "@/components/configurator/AttributeRenderer";
import { AIPreviewPanel } from "@/components/ai/AIPreviewPanel";
import { ReviewForm } from "@/components/reviews/ReviewForm";
import { ReviewList } from "@/components/reviews/ReviewList";
import { StarRating } from "@/components/reviews/StarRating";
import Link from "next/link";
import { Heart, ShoppingCart, Loader2, ArrowLeft, Image as ImageIcon, Sparkles, MessageSquare } from "lucide-react";

interface Product {
  _id: string;
  category_id: string;
  title: string;
  slug: string;
  type: "pre_designed" | "fully_custom";
  base_price: number;
  images: string[];
  thumbnail: string;
  description: string;
  specifications: Record<string, string>;
  default_attributes: Record<string, string | number | boolean>;
  stock_status: "in_stock" | "made_to_order" | "out_of_stock";
  rating_avg: number;
  rating_count: number;
  category: {
    _id: string;
    name: string;
    attribute_schema: AttributeField[];
    accent_color: "pink" | "blue" | "violet" | "yellow";
  };
}

interface PriceBreakdownItem {
  name: string;
  price: number;
}

export default function ProductDetailPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = use(params);
  const { user, isAuthenticated } = useAuth();
  const { showToast } = useToast();

  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  
  // Configurator states
  const [attributes, setAttributes] = useState<Record<string, string | number | boolean>>({});
  const [qty, setQty] = useState<number>(1);
  const [totalPrice, setTotalPrice] = useState<number>(0);
  const [priceBreakdown, setPriceBreakdown] = useState<PriceBreakdownItem[]>([]);
  
  // View mode tab states (Photos vs AI Preview)
  const [viewMode, setViewMode] = useState<"photos" | "ai">("photos");
  const [aiPreviewUrl, setAiPreviewUrl] = useState<string | null>(null);
  const [activePhotoIdx, setActivePhotoIdx] = useState<number>(0);
  
  // Wishlist state
  const [isWishlisted, setIsWishlisted] = useState<boolean>(false);
  const [wishlistLoading, setWishlistLoading] = useState<boolean>(false);
  const [refreshReviews, setRefreshReviews] = useState<number>(0);

  // Fetch Product details
  useEffect(() => {
    const fetchProduct = async () => {
      try {
        const res = await api.get(`/products/${slug}`);
        if (res.success && res.data) {
          const prod: Product = res.data;
          setProduct(prod);
          setAttributes(prod.default_attributes || {});
          setTotalPrice(prod.base_price);
        } else {
          showToast(res.message || "Failed to load product details", "error");
        }
      } catch (err) {
        console.error(err);
        showToast("Error connecting to catalog services", "error");
      } finally {
        setLoading(false);
      }
    };
    fetchProduct();
  }, [slug, showToast]);

  // Recalculate price in real-time when attributes update
  useEffect(() => {
    if (!product) return;
    
    // Call Pricing API
    const calculatePrice = async () => {
      try {
        const res = await api.post("/configurator/price", {
          product_id: product._id,
          selected_attributes: attributes
        });
        if (res.success && res.data) {
          setTotalPrice(res.data.total_price);
          setPriceBreakdown(res.data.breakdown || []);
        }
      } catch (e) {
        // Fallback local pricing math if offline
        let localTotal = product.base_price;
        const schema = product.category?.attribute_schema || [];
        schema.forEach((field) => {
          const val = attributes[field.key];
          if (val && field.options) {
            const opt = field.options.find((o) => o.value === val);
            if (opt?.price_delta) localTotal += opt.price_delta;
          }
        });
        setTotalPrice(localTotal);
      }
    };
    
    calculatePrice();
  }, [attributes, product]);

  // Wishlist handlers
  useEffect(() => {
    if (isAuthenticated && product) {
      const checkWishlist = async () => {
        try {
          const res = await api.get("/wishlist");
          if (res.success && res.data) {
            const ids = res.data.map((p: any) => p._id);
            setIsWishlisted(ids.includes(product._id));
          }
        } catch {}
      };
      checkWishlist();
    }
  }, [isAuthenticated, product]);

  const handleWishlistToggle = async () => {
    if (!isAuthenticated) {
      showToast("Please login to manage your wishlist", "warning");
      return;
    }
    if (!product || wishlistLoading) return;
    
    setWishlistLoading(true);
    try {
      if (isWishlisted) {
        const res = await api.delete(`/wishlist/${product._id}`);
        if (res.success) {
          setIsWishlisted(false);
          showToast("Removed from wishlist", "info");
        }
      } else {
        const res = await api.post(`/wishlist/${product._id}`);
        if (res.success) {
          setIsWishlisted(true);
          showToast("Added to wishlist!", "success");
        }
      }
    } catch {
      showToast("Wishlist action failed", "error");
    } finally {
      setWishlistLoading(false);
    }
  };

  const handleAttributeChange = (key: string, value: any) => {
    setAttributes((prev) => ({
      ...prev,
      [key]: value
    }));
  };

  const handleAddToCart = async () => {
    if (!isAuthenticated) {
      showToast("Authentication required to add items to cart", "warning");
      return;
    }
    if (!product) return;

    try {
      const res = await api.post("/cart/items", {
        product_id: product._id,
        selected_attributes: attributes,
        quantity: qty,
        ai_preview_image: aiPreviewUrl,
        custom_text: attributes.text || ""
      });

      if (res.success) {
        showToast("Added configuration to your cart!", "success");
        // Dispatch event to shake cart header
        window.dispatchEvent(new Event("cart-updated"));
      } else {
        showToast(res.message || "Failed to add to cart", "error");
      }
    } catch {
      showToast("Network cart error occurred", "error");
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-void-black flex flex-col items-center justify-center text-text-muted text-sm gap-2">
        <Loader2 className="w-8 h-8 animate-spin text-neon-blue" />
        <span>Fetching category custom details...</span>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="min-h-screen bg-void-black text-text-primary p-10 flex flex-col items-center justify-center gap-4">
        <h2 className="text-xl font-bold">Catalog Product Not Found</h2>
        <Link href="/" className="text-neon-blue underline text-xs">Return to Homepage</Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-void-black text-text-primary pb-20 selection:bg-neon-pink selection:text-void-black">
      
      {/* Header persistent link */}
      <div className="max-w-6xl mx-auto px-6 pt-6">
        <Link href="/" className="inline-flex items-center gap-2 text-xs font-bold text-text-muted hover:text-neon-blue transition-colors cursor-pointer">
          <ArrowLeft className="w-4 h-4" /> BACK TO CATALOG
        </Link>
      </div>

      <div className="max-w-6xl mx-auto px-6 mt-6 grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        
        {/* Left Column: Media display / AI previews */}
        <div className="lg:col-span-6 flex flex-col gap-5">
          {/* Tab controls */}
          <div className="flex gap-2.5 p-1 rounded-xl bg-panel-charcoal/40 border border-panel-charcoal max-w-xs self-start">
            <button
              onClick={() => setViewMode("photos")}
              className={`px-4 py-2 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer ${
                viewMode === "photos" 
                  ? "bg-panel-charcoal text-neon-blue glow-blue" 
                  : "text-text-muted hover:text-text-primary"
              }`}
            >
              <ImageIcon className="w-4 h-4" /> PHOTOS
            </button>
            <button
              onClick={() => setViewMode("ai")}
              className={`px-4 py-2 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer ${
                viewMode === "ai" 
                  ? "bg-panel-charcoal text-neon-violet glow-violet" 
                  : "text-text-muted hover:text-text-primary"
              }`}
            >
              <Sparkles className="w-4 h-4" /> AI PREVIEW
            </button>
          </div>

          {/* Visual Canvas panel */}
          {viewMode === "photos" ? (
            <div className="flex flex-col gap-4">
              <div className="relative w-full h-[400px] bg-panel-charcoal/20 border border-panel-charcoal rounded-xl overflow-hidden flex items-center justify-center">
                {product.images && product.images.length > 0 ? (
                  <img
                    src={product.images[activePhotoIdx]}
                    alt={product.title}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <span className="text-text-muted text-xs">No product images uploaded</span>
                )}
                
                {/* Out of stock tag */}
                {product.stock_status === "out_of_stock" && (
                  <span className="absolute top-4 left-4 bg-neon-pink text-void-black text-[10px] font-black uppercase px-2.5 py-1 rounded">
                    OUT OF STOCK
                  </span>
                )}
              </div>

              {/* Thumbnails */}
              {product.images && product.images.length > 1 && (
                <div className="flex gap-3">
                  {product.images.map((img, idx) => (
                    <button
                      key={idx}
                      onClick={() => setActivePhotoIdx(idx)}
                      className={`w-16 h-16 rounded-lg overflow-hidden border transition-colors cursor-pointer ${
                        activePhotoIdx === idx ? "border-neon-blue" : "border-panel-charcoal"
                      }`}
                    >
                      <img src={img} alt="thumb" className="w-full h-full object-cover" />
                    </button>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <AIPreviewPanel
              categoryId={product.category_id}
              selectedAttributes={attributes}
              savedPreviewUrl={aiPreviewUrl}
              onPreviewGenerated={setAiPreviewUrl}
            />
          )}

          {/* Product Descriptions & Details */}
          <div className="mt-4 flex flex-col gap-4">
            <h1 className="text-2xl font-black uppercase tracking-tight">{product.title}</h1>
            
            {/* Reviews Rollup Display */}
            {product.rating_count > 0 && (
              <div className="flex items-center gap-2">
                <StarRating rating={product.rating_avg} size={14} />
                <span className="text-xs text-text-muted">
                  {product.rating_avg} out of 5 ({product.rating_count} reviews)
                </span>
              </div>
            )}

            <p className="text-sm text-text-muted leading-relaxed">{product.description}</p>
            
            {/* Specs */}
            {product.specifications && Object.keys(product.specifications).length > 0 && (
              <div className="border-t border-panel-charcoal/50 pt-4 flex flex-col gap-2">
                <h4 className="text-xs font-bold text-text-primary uppercase tracking-wider">Specifications</h4>
                <div className="grid grid-cols-2 gap-y-2 gap-x-4 text-xs mt-1">
                  {Object.entries(product.specifications).map(([k, v]) => (
                    <div key={k} className="flex flex-col">
                      <span className="text-text-muted">{k}</span>
                      <span className="text-text-primary font-semibold mt-0.5">{v}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Schema Configurator Inputs */}
        <div className="lg:col-span-6 flex flex-col gap-6">
          <div className="p-6 rounded-2xl bg-panel-charcoal/20 border border-panel-charcoal flex flex-col gap-6">
            <h3 className="text-base font-bold text-text-primary uppercase border-b border-panel-charcoal pb-3 flex items-center justify-between">
              Configure Options
              <span className="text-[10px] text-text-muted lowercase">step-by-step</span>
            </h3>

            {/* Render Schema Attributes */}
            {product.category?.attribute_schema && product.category.attribute_schema.length > 0 ? (
              <div className="flex flex-col gap-5">
                {product.category.attribute_schema
                  .sort((a, b) => (a.display_order || 0) - (b.display_order || 0))
                  .map((field) => (
                    <AttributeRenderer
                      key={field.key}
                      field={field}
                      value={attributes[field.key]}
                      onChange={(val) => handleAttributeChange(field.key, val)}
                    />
                  ))}
              </div>
            ) : (
              <div className="py-8 text-center text-xs text-text-muted">
                No custom configuration settings needed for this product.
              </div>
            )}

            {/* Pricing calculations details */}
            <div className="border-t border-panel-charcoal pt-5 flex flex-col gap-3">
              <div className="flex items-baseline justify-between">
                <span className="text-sm font-bold text-text-muted">Estimated Total</span>
                <span className="text-2xl font-black text-neon-blue text-glow-blue animate-pulse">
                  ₹{totalPrice.toLocaleString("en-IN")}
                </span>
              </div>
              
              {/* Detailed Breakdown */}
              {priceBreakdown.length > 1 && (
                <div className="p-3.5 rounded-lg bg-void-black/40 border border-panel-charcoal/50 flex flex-col gap-1.5 text-[10px]">
                  {priceBreakdown.map((item, index) => (
                    <div key={index} className="flex justify-between text-text-muted">
                      <span>{item.name}</span>
                      <span className="font-semibold text-text-primary">₹{item.price}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* CTAs Action bar */}
            <div className="flex gap-3 mt-2">
              <button
                type="button"
                onClick={handleAddToCart}
                disabled={product.stock_status === "out_of_stock"}
                className="flex-1 p-4 rounded-xl bg-neon-blue hover:bg-neon-blue/80 text-void-black font-extrabold text-sm tracking-wider glow-blue-hover transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-30 disabled:pointer-events-none"
              >
                <ShoppingCart className="w-4 h-4" /> ADD TO CART
              </button>
              
              <button
                type="button"
                onClick={handleWishlistToggle}
                className={`p-4 rounded-xl border flex items-center justify-center transition-all cursor-pointer ${
                  isWishlisted 
                    ? "border-neon-pink text-neon-pink bg-neon-pink/10 glow-pink" 
                    : "border-panel-charcoal text-text-muted hover:text-text-primary hover:border-text-muted/30"
                }`}
                title="Wishlist Toggle"
              >
                <Heart className="w-5 h-5 fill-current" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Reviews and Ratings segment */}
      <div className="max-w-6xl mx-auto px-6 mt-16 pt-8 border-t border-panel-charcoal/50 grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Left Column: Review Form (Only for eligible purchasers) */}
        <div className="lg:col-span-5">
          {isAuthenticated ? (
            <ReviewForm productId={product._id} onSuccess={() => setRefreshReviews(prev => prev + 1)} />
          ) : (
            <div className="p-6 rounded-xl glass-panel border border-panel-charcoal text-center flex flex-col items-center gap-3">
              <MessageSquare className="w-8 h-8 text-neon-violet opacity-55" />
              <h3 className="font-bold text-sm text-text-primary">Share your feedback</h3>
              <p className="text-xs text-text-muted">
                To leave a review, you must be logged in with an account containing a delivered purchase of this product.
              </p>
              <Link
                href="/login"
                className="mt-2 px-5 py-2.5 rounded bg-panel-charcoal hover:bg-void-black border border-neon-violet/30 hover:border-neon-violet/50 text-neon-violet text-xs font-bold transition-all cursor-pointer"
              >
                LOG IN TO LEAVE REVIEW
              </Link>
            </div>
          )}
        </div>

        {/* Right Column: Review List */}
        <div className="lg:col-span-7 flex flex-col gap-4">
          <ReviewList productId={product._id} refreshTrigger={refreshReviews} />
        </div>
      </div>
    </div>
  );
}

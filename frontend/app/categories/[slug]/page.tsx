"use client";

import React, { useState, useEffect, use } from "react";
import { api } from "@/lib/api";
import { useToast } from "@/context/ToastContext";
import Link from "next/link";
import { Loader2, ArrowLeft, Eye } from "lucide-react";

interface Product {
  _id: string;
  title: string;
  slug: string;
  thumbnail: string;
  base_price: number;
  rating_avg: number;
  rating_count: number;
  stock_status: string;
}

interface Category {
  _id: string;
  name: string;
  description: string;
  accent_color: string;
}

export default function CategoryDetailPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = use(params);
  const { showToast } = useToast();

  const [category, setCategory] = useState<Category | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch products by category slug
        const res = await api.get(`/products?category_slug=${slug}`);
        if (res.success && res.data) {
          setProducts(res.data.products || []);
          
          // Get category metadata from the first product or details
          if (res.data.products?.length > 0 && res.data.products[0].category) {
            setCategory(res.data.products[0].category);
          } else {
            // Retrieve categories list and find matching
            const catRes = await api.get("/categories");
            if (catRes.success && catRes.data) {
              const matched = catRes.data.find((c: any) => c.slug === slug);
              if (matched) setCategory(matched);
            }
          }
        }
      } catch {
        showToast("Error retrieving category catalog", "error");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [slug, showToast]);

  const getAccentGlowClass = (color: string) => {
    switch (color) {
      case "pink": return "text-neon-pink drop-shadow-[0_0_8px_#FF2E8A]";
      case "violet": return "text-neon-violet drop-shadow-[0_0_8px_#9B5CFF]";
      case "yellow": return "text-neon-yellow drop-shadow-[0_0_8px_#FFD118]";
      default: return "text-neon-blue drop-shadow-[0_0_8px_#18E7FF]";
    }
  };

  const getAccentBorderClass = (color: string) => {
    switch (color) {
      case "pink": return "hover:border-neon-pink/40";
      case "violet": return "hover:border-neon-violet/40";
      case "yellow": return "hover:border-neon-yellow/40";
      default: return "hover:border-neon-blue/40";
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-void-black flex flex-col items-center justify-center text-text-muted text-sm gap-2">
        <Loader2 className="w-8 h-8 animate-spin text-neon-blue" />
        <span>Loading catalog listing...</span>
      </div>
    );
  }

  if (!category && products.length === 0) {
    return (
      <div className="min-h-screen bg-void-black text-text-primary p-10 flex flex-col items-center justify-center gap-4">
        <h2 className="text-xl font-bold">Category Not Found</h2>
        <Link href="/" className="text-neon-blue underline text-xs">Return to Homepage</Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-void-black text-text-primary p-6 md:p-10 selection:bg-neon-pink selection:text-void-black">
      <div className="max-w-6xl mx-auto flex flex-col gap-6">
        
        {/* Header */}
        <div className="border-b border-panel-charcoal pb-5">
          <Link href="/" className="inline-flex items-center gap-1.5 text-xs text-text-muted hover:text-neon-blue font-bold mb-3">
            <ArrowLeft className="w-4 h-4" /> Back to Store
          </Link>
          <h1 className="text-2xl font-black uppercase tracking-tight flex items-center gap-2">
            Category: <span className={getAccentGlowClass(category?.accent_color || "blue")}>{category?.name || slug}</span>
          </h1>
          <p className="text-xs text-text-muted mt-1 max-w-xl leading-relaxed">
            {category?.description || "Browse premium lighting and custom art pieces crafted to order."}
          </p>
        </div>

        {products.length === 0 ? (
          <div className="py-20 text-center text-text-muted">
            No products uploaded under this category yet.
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6 mt-2">
            {products.map((item) => (
              <div
                key={item._id}
                className={`rounded-2xl border border-panel-charcoal bg-panel-charcoal/20 overflow-hidden group transition-colors flex flex-col justify-between ${getAccentBorderClass(category?.accent_color || "blue")}`}
              >
                {/* Thumbnail */}
                <div className="relative h-48 bg-void-black overflow-hidden">
                  <img
                    src={item.thumbnail || "/globe.svg"}
                    alt={item.title}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                  {item.stock_status === "out_of_stock" && (
                    <span className="absolute top-3 left-3 bg-neon-pink text-void-black text-[9px] font-black uppercase px-2 py-0.5 rounded">
                      Out of stock
                    </span>
                  )}
                </div>

                {/* Details */}
                <div className="p-4 flex flex-col gap-3 flex-1 justify-between">
                  <div>
                    <h3 className="font-black text-sm text-glow-hover text-text-primary transition-colors line-clamp-1">
                      {item.title}
                    </h3>
                  </div>

                  <div className="flex justify-between items-center border-t border-panel-charcoal/45 pt-3 mt-1">
                    <span className="text-xs font-black text-text-primary">
                      From ₹{item.base_price.toLocaleString("en-IN")}
                    </span>

                    <Link
                      href={`/products/${item.slug}`}
                      className="px-3.5 py-1.5 rounded-lg bg-panel-charcoal hover:bg-void-black border border-panel-charcoal text-[10px] font-bold transition-all cursor-pointer flex items-center gap-1 text-text-muted hover:text-text-primary"
                    >
                      <Eye className="w-3.5 h-3.5" /> DESIGN
                    </Link>
                  </div>
                </div>

              </div>
            ))}
          </div>
        )}

      </div>
    </div>
  );
}

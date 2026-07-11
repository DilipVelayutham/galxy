"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Sparkles, Loader2, AlertCircle, RefreshCw } from "lucide-react";

interface Category {
  slug: string;
  name: string;
  short_tagline: string;
  description: string;
  cover_image: string;
  accent_color: string;
  display_order: number;
}

export default function CategoriesPage() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchCategories = async () => {
    await Promise.resolve();
    setLoading(true);
    setError(null);
    try {
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000";
      const res = await fetch(`${baseUrl}/api/categories`);
      if (!res.ok) {
        throw new Error(`Failed to load categories (Status ${res.status})`);
      }
      const json = await res.json();
      if (json.success && Array.isArray(json.data)) {
        setCategories(json.data);
      } else {
        throw new Error(json.message || "Invalid response format from API");
      }
    } catch (err: unknown) {
      console.error("Fetch categories error:", err);
      const errorMessage = err instanceof Error ? err.message : "Something went wrong while loading categories.";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchCategories();
    }, 0);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="flex-1 w-full max-w-7xl mx-auto px-4 py-12 md:py-16 flex flex-col justify-start">
      {/* Header Section */}
      <div className="text-center mb-12 md:mb-16">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-purple-500/30 bg-purple-500/10 text-purple-400 text-xs font-semibold uppercase tracking-wider mb-4 animate-pulse">
          <Sparkles className="w-3.5 h-3.5" />
          Custom Configurator
        </div>
        <h1 className="text-4xl md:text-5xl lg:text-6xl font-extrabold tracking-tight bg-gradient-to-r from-white via-gray-200 to-purple-400 bg-clip-text text-transparent mb-4">
          Personalized Product Categories
        </h1>
        <p className="text-gray-400 text-lg max-w-2xl mx-auto">
          Choose a dynamic category below to design, custom-tailor, and preview your bespoke creation.
        </p>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="flex-1 flex flex-col items-center justify-center py-20">
          <Loader2 className="w-12 h-12 text-purple-500 animate-spin mb-4" />
          <p className="text-gray-400 text-sm font-medium animate-pulse">
            Connecting to GALXY service, loading categories...
          </p>
        </div>
      )}

      {/* Error State */}
      {error && !loading && (
        <div className="flex-1 flex flex-col items-center justify-center max-w-md mx-auto py-12 px-6 rounded-2xl glass-panel border border-red-500/20 text-center">
          <AlertCircle className="w-12 h-12 text-red-400 mb-4" />
          <h3 className="text-lg font-bold text-white mb-2">Service Connection Error</h3>
          <p className="text-gray-400 text-sm mb-6">{error}</p>
          <button
            onClick={fetchCategories}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-red-500/10 hover:bg-red-500/20 border border-red-500/30 hover:border-red-500/50 text-red-200 font-semibold text-sm transition-all duration-200"
          >
            <RefreshCw className="w-4 h-4" />
            Retry Connection
          </button>
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && categories.length === 0 && (
        <div className="flex-1 flex flex-col items-center justify-center py-20 text-center">
          <div className="w-16 h-16 rounded-2xl bg-gray-900 border border-gray-800 flex items-center justify-center mb-4">
            <Sparkles className="w-8 h-8 text-gray-500" />
          </div>
          <h3 className="text-lg font-bold text-white mb-1">No Categories Found</h3>
          <p className="text-gray-400 text-sm max-w-xs">
            There are currently no active configurator categories available.
          </p>
        </div>
      )}

      {/* Categories Grid */}
      {!loading && !error && categories.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 md:gap-8">
          {categories.map((category) => {
            // Accent colors theme mapping
            const colorClass = `accent-${category.accent_color || "neon_pink"}`;
            
            return (
              <Link
                key={category.slug}
                href={`/categories/${category.slug}`}
                className={`group relative flex flex-col rounded-2xl overflow-hidden glass-panel border border-white/5 hover:border-white/10 transition-all duration-300 hover:-translate-y-1.5 hover:shadow-2xl ${colorClass}`}
              >
                {/* Glow border overlay effect */}
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_0%,var(--accent-glow),transparent_60%)] opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />
                
                {/* Accent border highlight */}
                <div className="absolute top-0 inset-x-0 h-[2px] bg-gradient-to-r from-transparent via-[var(--accent)] to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />

                {/* Cover Image Container */}
                <div className="relative aspect-video w-full overflow-hidden bg-gray-900">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={category.cover_image}
                    alt={category.name}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500 ease-out"
                    loading="lazy"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-[#05020c] via-[#05020c]/40 to-transparent" />
                </div>

                {/* Content */}
                <div className="flex-1 p-5 md:p-6 flex flex-col justify-between relative z-10">
                  <div>
                    <h3 className="text-xl font-bold text-white group-hover:text-[var(--accent-text)] transition-colors duration-200 mb-2">
                      {category.name}
                    </h3>
                    <p className="text-purple-400/80 text-xs font-semibold tracking-wide uppercase mb-3">
                      {category.short_tagline}
                    </p>
                    <p className="text-gray-400 text-sm line-clamp-3 leading-relaxed">
                      {category.description}
                    </p>
                  </div>

                  <div className="mt-6 pt-4 border-t border-white/5 flex items-center justify-between">
                    <span className="text-xs text-gray-500 font-medium">Customize Now</span>
                    <span className="text-xs font-bold text-[var(--accent-text)] group-hover:underline flex items-center gap-1">
                      Configure →
                    </span>
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}

"use client";

import React, { useState, useEffect } from "react";
import { api } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { useToast } from "@/context/ToastContext";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Heart, Trash2, ArrowLeft, ArrowRight, Loader2 } from "lucide-react";

interface Product {
  _id: string;
  title: string;
  slug: string;
  base_price: number;
  thumbnail: string;
  description: string;
}

export default function WishlistPage() {
  const { isAuthenticated, loading: authLoading } = useAuth();
  const { showToast } = useToast();
  const router = useRouter();

  const [wishlist, setWishlist] = useState<Product[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const fetchWishlist = async () => {
    setLoading(true);
    try {
      const res = await api.get("/wishlist");
      if (res.success && res.data) {
        setWishlist(res.data);
      }
    } catch {
      showToast("Error loading wishlist", "error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!authLoading) {
      if (!isAuthenticated) {
        showToast("Please login to view your wishlist", "warning");
        router.push("/login");
      } else {
        fetchWishlist();
      }
    }
  }, [isAuthenticated, authLoading, router]);

  const handleRemove = async (prodId: string) => {
    setDeletingId(prodId);
    try {
      const res = await api.delete(`/wishlist/${prodId}`);
      if (res.success) {
        showToast("Removed from wishlist", "info");
        setWishlist((prev) => prev.filter((p) => p._id !== prodId));
      } else {
        showToast(res.message || "Failed to remove item", "error");
      }
    } catch {
      showToast("Network wishlist error", "error");
    } finally {
      setDeletingId(null);
    }
  };

  if (authLoading || loading) {
    return (
      <div className="min-h-screen bg-void-black flex flex-col items-center justify-center text-text-muted text-sm gap-2">
        <Loader2 className="w-8 h-8 animate-spin text-neon-pink" />
        <span>Loading your wishlisted configurations...</span>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-void-black text-text-primary p-6 md:p-10 selection:bg-neon-pink selection:text-void-black">
      <div className="max-w-4xl mx-auto flex flex-col gap-6">
        
        {/* Header */}
        <div className="flex justify-between items-center border-b border-panel-charcoal/50 pb-4">
          <h1 className="text-2xl font-black uppercase tracking-tight flex items-center gap-2">
            <Heart className="w-6 h-6 text-neon-pink fill-current drop-shadow-[0_0_8px_#FF2E8A]" />
            My Wishlist
          </h1>
          
          <Link href="/" className="inline-flex items-center gap-1.5 text-xs text-text-muted hover:text-neon-pink font-bold">
            <ArrowLeft className="w-4 h-4" /> Back to Catalog
          </Link>
        </div>

        {wishlist.length === 0 ? (
          <div className="py-20 text-center rounded-xl bg-panel-charcoal/20 border border-panel-charcoal text-text-muted flex flex-col items-center gap-3">
            <Heart className="w-12 h-12 opacity-35 text-neon-pink" />
            <p className="font-bold text-sm">Your wishlist is empty</p>
            <p className="text-xs">Save your customized lighting styles for later by tapping the heart icon on any detail page.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
            {wishlist.map((item) => (
              <div key={item._id} className="rounded-2xl border border-panel-charcoal bg-panel-charcoal/20 overflow-hidden group hover:border-neon-pink/40 transition-colors flex flex-col justify-between">
                
                {/* Image */}
                <div className="relative h-44 bg-void-black overflow-hidden">
                  <img
                    src={item.thumbnail || "/globe.svg"}
                    alt={item.title}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                </div>

                {/* Details */}
                <div className="p-4 flex flex-col gap-3 flex-1 justify-between">
                  <div>
                    <h3 className="font-black text-sm text-text-primary group-hover:text-neon-pink transition-colors line-clamp-1">
                      {item.title}
                    </h3>
                    <p className="text-xs text-text-muted mt-1 line-clamp-2 leading-relaxed">
                      {item.description}
                    </p>
                  </div>

                  <div className="flex justify-between items-center border-t border-panel-charcoal/45 pt-3 mt-1">
                    <span className="text-sm font-black text-neon-pink">
                      ₹{item.base_price.toLocaleString("en-IN")}
                    </span>

                    <div className="flex gap-2">
                      <button
                        onClick={() => handleRemove(item._id)}
                        disabled={deletingId === item._id}
                        className="p-2 rounded bg-panel-charcoal text-text-muted hover:text-neon-pink cursor-pointer disabled:opacity-40"
                        title="Remove from wishlist"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                      <Link
                        href={`/products/${item.slug}`}
                        className="p-2 rounded bg-neon-pink text-void-black font-black hover:opacity-85 cursor-pointer flex items-center justify-center"
                        title="Configure Design"
                      >
                        <ArrowRight className="w-3.5 h-3.5" />
                      </Link>
                    </div>
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

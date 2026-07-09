"use client";

import React, { useState, useEffect } from "react";
import { api } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import { useToast } from "@/context/ToastContext";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Trash2, ShoppingBag, Plus, Minus, ArrowRight, Loader2, RefreshCw } from "lucide-react";

interface CartItem {
  id: string;
  product_id: string;
  category_id: string;
  selected_attributes: Record<string, any>;
  quantity: number;
  unit_price_estimate: number;
  ai_preview_image: string | null;
  custom_text: string;
  is_available: boolean;
  needs_attention: boolean;
  message?: string;
}

export default function CartPage() {
  const { isAuthenticated, loading: authLoading } = useAuth();
  const { showToast } = useToast();
  const router = useRouter();

  const [cartItems, setCartItems] = useState<CartItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [mutatingId, setMutatingId] = useState<string | null>(null);

  const fetchCart = async () => {
    setLoading(true);
    try {
      const res = await api.get("/cart");
      if (res.success && res.data) {
        setCartItems(res.data.items || []);
      }
    } catch {
      showToast("Error loading shopping cart", "error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!authLoading) {
      if (!isAuthenticated) {
        showToast("Please login to view your cart", "warning");
        router.push("/login");
      } else {
        fetchCart();
      }
    }
  }, [isAuthenticated, authLoading, router]);

  const handleUpdateQty = async (itemId: string, currentQty: number, change: number) => {
    const newQty = currentQty + change;
    if (newQty < 1) return;

    setMutatingId(itemId);
    try {
      const res = await api.put(`/cart/items/${itemId}`, { quantity: newQty });
      if (res.success) {
        showToast("Cart updated", "success");
        // Optimistic UI update or refresh
        setCartItems((prev) =>
          prev.map((item) => (item.id === itemId ? { ...item, quantity: newQty } : item))
        );
      } else {
        showToast(res.message || "Failed to update quantity", "error");
      }
    } catch {
      showToast("Network update error", "error");
    } finally {
      setMutatingId(null);
    }
  };

  const handleDeleteItem = async (itemId: string) => {
    setMutatingId(itemId);
    try {
      const res = await api.delete(`/cart/items/${itemId}`);
      if (res.success) {
        showToast("Item removed from cart", "info");
        setCartItems((prev) => prev.filter((item) => item.id !== itemId));
      } else {
        showToast(res.message || "Failed to remove item", "error");
      }
    } catch {
      showToast("Network removal error", "error");
    } finally {
      setMutatingId(null);
    }
  };

  const handleClearCart = async () => {
    if (!confirm("Are you sure you want to empty your cart?")) return;
    setLoading(true);
    try {
      const res = await api.delete("/cart/clear");
      if (res.success) {
        showToast("Cart cleared", "info");
        setCartItems([]);
      }
    } catch {
      showToast("Network clearing error", "error");
    } finally {
      setLoading(false);
    }
  };

  const getCartTotal = () => {
    return cartItems.reduce((acc, curr) => {
      if (!curr.is_available) return acc;
      return acc + curr.unit_price_estimate * curr.quantity;
    }, 0);
  };

  if (authLoading || loading) {
    return (
      <div className="min-h-screen bg-void-black flex flex-col items-center justify-center text-text-muted text-sm gap-2">
        <Loader2 className="w-8 h-8 animate-spin text-neon-blue" />
        <span>Loading your customized basket...</span>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-void-black text-text-primary p-6 md:p-10 selection:bg-neon-pink selection:text-void-black">
      <div className="max-w-4xl mx-auto flex flex-col gap-6">
        
        {/* Header */}
        <div className="flex justify-between items-center border-b border-panel-charcoal pb-4">
          <h1 className="text-2xl font-black uppercase tracking-tight flex items-center gap-2">
            <ShoppingBag className="w-6 h-6 text-neon-blue drop-shadow-[0_0_8px_#18E7FF]" />
            Shopping Cart
          </h1>

          {cartItems.length > 0 && (
            <button
              onClick={handleClearCart}
              className="text-xs font-bold text-neon-pink hover:underline cursor-pointer"
            >
              Clear Basket
            </button>
          )}
        </div>

        {cartItems.length === 0 ? (
          <div className="py-20 text-center rounded-xl bg-panel-charcoal/20 border border-panel-charcoal text-text-muted flex flex-col items-center gap-3">
            <ShoppingBag className="w-12 h-12 opacity-35 text-neon-blue" />
            <p className="font-bold text-sm">Your shopping cart is empty</p>
            <p className="text-xs">Browse our custom categories to design your bespoke neon lights or quilled frames!</p>
            <Link
              href="/"
              className="mt-2 px-5 py-2.5 rounded bg-panel-charcoal hover:bg-void-black border border-neon-blue/40 text-neon-blue text-xs font-bold transition-all cursor-pointer"
            >
              BROWSE CATALOG
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            
            {/* Items list */}
            <div className="lg:col-span-8 flex flex-col gap-4">
              {cartItems.map((item) => (
                <div
                  key={item.id}
                  className={`p-5 rounded-xl border bg-panel-charcoal/20 flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between ${
                    !item.is_available ? "border-neon-pink/20 bg-neon-pink/[0.01]" : "border-panel-charcoal"
                  }`}
                >
                  <div className="flex gap-4 items-center">
                    {/* Preview Image */}
                    <div className="w-16 h-16 rounded-lg bg-void-black overflow-hidden border border-panel-charcoal flex-shrink-0">
                      <img
                        src={item.ai_preview_image || "/vercel.svg"}
                        alt="Cart item preview"
                        className="w-full h-full object-cover"
                      />
                    </div>

                    {/* Attributes description */}
                    <div className="min-w-0">
                      <h4 className="font-bold text-sm text-text-primary">
                        {item.custom_text ? `Custom Design: "${item.custom_text}"` : "Custom Item Inquiry"}
                      </h4>
                      
                      <div className="flex flex-wrap gap-x-2 gap-y-1 mt-1 text-[10px] text-text-muted">
                        {Object.entries(item.selected_attributes).map(([k, v]) => (
                          <span key={k} className="bg-panel-charcoal px-1.5 py-0.5 rounded uppercase">
                            {k}: {String(v)}
                          </span>
                        ))}
                      </div>

                      {/* Stale warnings */}
                      {item.message && (
                        <p className={`text-[10px] font-bold mt-1.5 ${item.needs_attention ? "text-neon-yellow" : "text-neon-pink"}`}>
                          * {item.message}
                        </p>
                      )}
                    </div>
                  </div>

                  {/* Qty & Price controls */}
                  <div className="flex items-center justify-between sm:justify-end gap-6 w-full sm:w-auto pt-3 sm:pt-0 border-t sm:border-t-0 border-panel-charcoal/45">
                    {item.is_available && (
                      <div className="flex items-center border border-panel-charcoal bg-void-black rounded-lg p-1.5 gap-2.5">
                        <button
                          onClick={() => handleUpdateQty(item.id, item.quantity, -1)}
                          disabled={item.quantity <= 1 || mutatingId === item.id}
                          className="text-text-muted hover:text-text-primary disabled:opacity-20 cursor-pointer"
                        >
                          <Minus className="w-3.5 h-3.5" />
                        </button>
                        <span className="text-xs font-bold w-4 text-center">{item.quantity}</span>
                        <button
                          onClick={() => handleUpdateQty(item.id, item.quantity, 1)}
                          disabled={mutatingId === item.id}
                          className="text-text-muted hover:text-text-primary disabled:opacity-20 cursor-pointer"
                        >
                          <Plus className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    )}

                    <div className="flex flex-col items-end">
                      <span className="text-sm font-black text-neon-blue">
                        ₹{(item.unit_price_estimate * item.quantity).toLocaleString("en-IN")}
                      </span>
                      <button
                        onClick={() => handleDeleteItem(item.id)}
                        disabled={mutatingId === item.id}
                        className="text-text-muted hover:text-neon-pink mt-1 cursor-pointer transition-colors"
                        title="Remove item"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Price Summary card */}
            <div className="lg:col-span-4 p-6 rounded-2xl bg-panel-charcoal border border-panel-charcoal flex flex-col gap-6">
              <h3 className="text-sm font-bold uppercase tracking-wider text-text-primary border-b border-panel-charcoal/50 pb-3">
                Order Summary
              </h3>

              <div className="flex justify-between items-baseline">
                <span className="text-xs text-text-muted font-bold">Estimated Total</span>
                <span className="text-2xl font-black text-neon-blue text-glow-blue">
                  ₹{getCartTotal().toLocaleString("en-IN")}
                </span>
              </div>

              <p className="text-[10px] text-text-muted leading-relaxed">
                * Prices are estimates based on default configurations. Asil will confirm the final quoted price via offline chat during confirmation.
              </p>

              <Link
                href="/checkout"
                className="w-full p-4 rounded-xl bg-neon-blue hover:bg-neon-blue/80 text-void-black font-extrabold text-sm tracking-wider glow-blue-hover transition-all flex items-center justify-center gap-2 cursor-pointer"
              >
                PROCEED TO CHECKOUT <ArrowRight className="w-4 h-4" />
              </Link>
            </div>

          </div>
        )}

      </div>
    </div>
  );
}

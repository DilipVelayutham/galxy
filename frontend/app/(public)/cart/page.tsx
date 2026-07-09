'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '../../../context/AuthContext';
import { Trash2, AlertTriangle, ShieldAlert, ShoppingBag, ArrowRight, RefreshCw, Sparkles, CheckCircle2 } from 'lucide-react';
import Link from 'next/link';
import Header from '../../../components/Header';

interface CartItem {
  _id: string;
  product_id: string;
  category_id: string;
  product_title: string;
  category_name: string;
  thumbnail: string;
  selected_attributes: Record<string, string | number | boolean>;
  quantity: number;
  unit_price_estimate: number;
  line_total_estimate: number;
  price_breakdown: Array<{ label: string; delta: number }>;
  ai_preview_image: string | null;
  custom_text: string | null;
  added_at: string;
  updated_at: string;
  is_available: boolean;
  needs_attention: boolean;
  stale_reason?: string;
}

export default function CartPage() {
  const { user, loading: userLoading, refreshCart, triggerToast } = useAuth();
  const [cartItems, setCartItems] = useState<CartItem[]>([]);
  const [subtotal, setSubtotal] = useState(0);
  const [loading, setLoading] = useState(true);

  // States for interactive Re-configure modal
  const [editingItem, setEditingItem] = useState<CartItem | null>(null);
  const [editedAttributes, setEditedAttributes] = useState<Record<string, string | number | boolean>>({});

  const fetchCartData = React.useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/cart');
      if (res.ok) {
        const result = await res.json();
        if (result.success && result.data) {
          setCartItems(result.data.items || []);
          setSubtotal(result.data.subtotal_estimate || 0);
        }
      }
    } catch (err) {
      console.error('Error fetching cart:', err);
      triggerToast('Error loading cart items', 'error');
    } finally {
      setLoading(false);
    }
  }, [triggerToast]);

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchCartData();
    }, 0);
    return () => clearTimeout(timer);
  }, [user, fetchCartData]);

  const handleUpdateQuantity = async (itemId: string, newQty: number) => {
    if (newQty <= 0) return;
    try {
      const res = await fetch(`/api/cart/items/${itemId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ quantity: newQty }),
      });
      if (res.ok) {
        const result = await res.json();
        if (result.success && result.data) {
          setCartItems(result.data.items);
          setSubtotal(result.data.subtotal_estimate);
          refreshCart();
          triggerToast('Quantity updated', 'success');
        }
      }
    } catch (err) {
      console.error(err);
      triggerToast('Failed to update quantity', 'error');
    }
  };

  const handleRemoveItem = async (itemId: string) => {
    try {
      const res = await fetch(`/api/cart/items/${itemId}`, {
        method: 'DELETE',
      });
      if (res.ok) {
        const result = await res.json();
        if (result.success && result.data) {
          setCartItems(result.data.items);
          setSubtotal(result.data.subtotal_estimate);
          refreshCart();
          triggerToast('Item removed from cart', 'success');
        }
      }
    } catch (err) {
      console.error(err);
      triggerToast('Failed to remove item', 'error');
    }
  };

  const handleClearCart = async () => {
    try {
      const res = await fetch('/api/cart/clear', {
        method: 'DELETE',
      });
      if (res.ok) {
        const result = await res.json();
        if (result.success && result.data) {
          setCartItems([]);
          setSubtotal(0);
          refreshCart();
          triggerToast('Cart cleared completely', 'success');
        }
      }
    } catch (err) {
      console.error(err);
      triggerToast('Failed to clear cart', 'error');
    }
  };

  // Re-configure Flow
  const openReconfigureModal = (item: CartItem) => {
    setEditingItem(item);
    setEditedAttributes(item.selected_attributes);
  };

  const handleSaveReconfigured = async () => {
    if (!editingItem) return;

    try {
      const res = await fetch(`/api/cart/items/${editingItem._id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          selected_attributes: editedAttributes
        }),
      });

      if (res.ok) {
        const result = await res.json();
        if (result.success && result.data) {
          setCartItems(result.data.items);
          setSubtotal(result.data.subtotal_estimate);
          setEditingItem(null);
          refreshCart();
          triggerToast('Product configuration successfully updated!', 'success');
        }
      }
    } catch (err) {
      console.error(err);
      triggerToast('Failed to save configuration', 'error');
    }
  };

  if (userLoading) {
    return (
      <div className="min-h-screen flex flex-col bg-bg-void text-text-primary">
        <Header />
        <div className="flex-1 flex flex-col items-center justify-center py-20">
          <div className="w-8 h-8 rounded-full border-2 border-neon-blue border-t-transparent animate-spin mb-4" />
          <span className="text-sm text-text-muted font-semibold">Loading...</span>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen flex flex-col bg-bg-void text-text-primary">
        <Header />
        <div className="flex-1 flex flex-col items-center justify-center p-8 max-w-md mx-auto text-center">
          <div className="w-16 h-16 rounded-full bg-neon-pink/10 border border-neon-pink flex items-center justify-center mb-6 shadow-glow-pink animate-pulse">
            <ShieldAlert size={28} className="text-neon-pink" />
          </div>
          <h2 className="text-2xl font-extrabold font-display mb-3 text-glow-pink">Authentication Required</h2>
          <p className="text-text-muted text-sm mb-6 leading-relaxed">
            Please log in to view and manage your shopping cart.
          </p>
          <Link
            href="/login"
            className="w-full py-3 px-6 rounded-lg font-bold bg-gradient-to-r from-neon-pink to-neon-violet text-[#F4F4F7] shadow-glow-pink transition-all duration-300 transform hover:scale-[1.02]"
          >
            Sign In / Create Account
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-bg-void text-text-primary">
      <Header />
      <div className="flex-1 py-12 px-6 max-w-6xl mx-auto w-full">
      <div className="flex justify-between items-center mb-10 border-b border-white/5 pb-6">
        <div>
          <h1 className="text-4xl font-extrabold font-display text-text-primary text-glow-blue tracking-tight">
            Your Shopping Cart
          </h1>
          <p className="text-text-muted text-sm mt-1">
            Persisted selections, server-verified pricing, and active status tracking
          </p>
        </div>
        {cartItems.length > 0 && (
          <button
            onClick={handleClearCart}
            className="text-xs font-semibold text-neon-pink uppercase tracking-widest hover:underline transition-all"
          >
            Clear All
          </button>
        )}
      </div>

      {loading ? (
        <div className="flex flex-col items-center justify-center py-20">
          <div className="w-8 h-8 rounded-full border-2 border-neon-blue border-t-transparent animate-spin mb-4" />
          <span className="text-sm text-text-muted font-semibold">Fetching cart data...</span>
        </div>
      ) : cartItems.length === 0 ? (
        <div className="text-center py-20 glass-panel rounded-xl border-white/5 flex flex-col items-center justify-center">
          <ShoppingBag size={48} className="text-text-muted mb-4" />
          <h3 className="text-xl font-bold text-text-primary mb-1">Your cart is empty</h3>
          <p className="text-text-muted text-sm mb-6 max-w-xs">
            Build and customize your Neon Boards, Moonlight Lamps, or Quilling Art.
          </p>
          <Link
            href="/products/custom-neon-sign"
            className="py-2.5 px-6 rounded-lg font-bold bg-neon-blue text-[#0B0B0F] shadow-glow-blue hover:brightness-110 transition-all duration-300"
          >
            Go to Configurator
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Cart List */}
          <div className="lg:col-span-8 flex flex-col gap-6">
            {cartItems.map((item) => {
              const hasErrors = !item.is_available || item.needs_attention;
              return (
                <div
                  key={item._id}
                  className={`relative rounded-xl overflow-hidden glass-panel border p-5 transition-all duration-300 ${
                    hasErrors 
                      ? 'border-neon-yellow/30 bg-neon-yellow/5' 
                      : 'border-white/5 hover:border-white/10'
                  }`}
                >
                  <div className="flex flex-col sm:flex-row gap-5">
                    {/* Item Thumbnail */}
                    <div className="relative w-24 h-24 rounded-lg overflow-hidden border border-white/10 flex-shrink-0">
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img
                        src={item.thumbnail}
                        alt={item.product_title}
                        className="w-full h-full object-cover"
                      />
                      {item.ai_preview_image && (
                        <span className="absolute top-1 left-1 bg-neon-pink text-[8px] font-extrabold uppercase px-1 py-0.5 rounded text-white flex items-center gap-0.5 shadow-md">
                          <Sparkles size={6} /> AI
                        </span>
                      )}
                    </div>

                    {/* Item Details */}
                    <div className="flex-1 flex flex-col justify-between">
                      <div>
                        <div className="flex justify-between items-start gap-4">
                          <div>
                            <span className="text-[10px] text-neon-blue font-extrabold uppercase tracking-wider block mb-0.5">
                              {item.category_name}
                            </span>
                            <h3 className="font-bold text-text-primary text-lg leading-tight">
                              {item.product_title}
                            </h3>
                          </div>
                          <span className="text-xl font-bold text-text-primary">
                            ₹{item.line_total_estimate}
                          </span>
                        </div>

                        {/* Custom Lettering Display */}
                        {item.custom_text && (
                          <div className="mt-2 text-xs font-semibold text-text-primary/95 flex gap-1.5 items-center">
                            <span className="text-text-muted">Lettering:</span>
                            <span className="bg-white/5 border border-white/10 rounded px-1.5 py-0.5 text-neon-pink font-mono">
                              &quot;{item.custom_text}&quot;
                            </span>
                          </div>
                        )}

                        {/* Attribute Badges */}
                        <div className="flex flex-wrap gap-1.5 mt-2.5">
                          {Object.entries(item.selected_attributes).map(([key, val]) => (
                            <span
                              key={key}
                              className="text-[10px] bg-white/5 border border-white/5 text-text-muted rounded-full px-2 py-0.5 capitalize font-medium"
                            >
                              {key}: {String(val)}
                            </span>
                          ))}
                        </div>
                      </div>

                      {/* Stale/Warning Banners */}
                      {!item.is_available && (
                        <div className="mt-4 p-3 rounded bg-neon-pink/10 border border-neon-pink/20 flex gap-2 items-center text-xs text-text-primary">
                          <AlertTriangle className="text-neon-pink flex-shrink-0" size={14} />
                          <div className="flex-1">
                            <span className="font-bold text-neon-pink block uppercase tracking-wider text-[9px] mb-0.5">Action Required</span>
                            {item.stale_reason || 'This product configuration is no longer active in our store.'}
                          </div>
                          <button
                            onClick={() => handleRemoveItem(item._id)}
                            className="bg-neon-pink text-void-black text-[10px] font-bold px-2 py-1 rounded hover:brightness-110 transition-all uppercase"
                          >
                            Remove
                          </button>
                        </div>
                      )}

                      {item.is_available && item.needs_attention && (
                        <div className="mt-4 p-3 rounded bg-neon-yellow/10 border border-neon-yellow/20 flex gap-2 items-center text-xs text-text-primary">
                          <AlertTriangle className="text-neon-yellow flex-shrink-0" size={14} />
                          <div className="flex-1">
                            <span className="font-bold text-neon-yellow block uppercase tracking-wider text-[9px] mb-0.5">Schema Outdated</span>
                            {item.stale_reason || 'Product configuration options have changed since this item was added.'}
                          </div>
                          <button
                            onClick={() => openReconfigureModal(item)}
                            className="bg-neon-yellow text-[#0B0B0F] text-[10px] font-bold px-2.5 py-1 rounded hover:brightness-110 transition-all uppercase"
                          >
                            Re-Configure
                          </button>
                        </div>
                      )}

                      {/* Controls Footer */}
                      <div className="flex justify-between items-center mt-4 border-t border-white/5 pt-3">
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-text-muted font-medium">Quantity:</span>
                          <div className="flex items-center border border-white/10 rounded-md bg-void-black overflow-hidden scale-90">
                            <button
                              type="button"
                              onClick={() => handleUpdateQuantity(item._id, item.quantity - 1)}
                              disabled={item.quantity <= 1 || !item.is_available}
                              className="px-2.5 py-1 hover:bg-white/5 text-text-primary disabled:opacity-30 transition-colors"
                            >
                              -
                            </button>
                            <span className="px-3.5 py-1 font-bold text-text-primary border-x border-white/10">
                              {item.quantity}
                            </span>
                            <button
                              type="button"
                              onClick={() => handleUpdateQuantity(item._id, item.quantity + 1)}
                              disabled={!item.is_available}
                              className="px-2.5 py-1 hover:bg-white/5 text-text-primary disabled:opacity-30 transition-colors"
                            >
                              +
                            </button>
                          </div>
                        </div>

                        <button
                          onClick={() => handleRemoveItem(item._id)}
                          className="text-text-muted hover:text-neon-pink p-1 transition-colors duration-200"
                          title="Remove item"
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Cart Summary */}
          <div className="lg:col-span-4 glass-panel border border-white/5 rounded-xl p-6 shadow-glow-blue sticky top-6">
            <h3 className="font-bold font-display text-xl text-text-primary mb-4 pb-2 border-b border-white/5">
              Order Inquiry Summary
            </h3>

            {/* Simulated Price Breakdown */}
            <div className="flex flex-col gap-3.5 text-sm mb-6">
              <div className="flex justify-between">
                <span className="text-text-muted">Item Subtotal</span>
                <span className="text-text-primary font-medium">₹{subtotal}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-text-muted">Estimated Shipping</span>
                <span className="text-neon-blue font-semibold uppercase tracking-wider text-xs">FREE (TBD offline)</span>
              </div>
              <div className="flex justify-between text-xs text-text-muted italic leading-normal">
                <span>Note: No online payments are processed. Pricing will be reviewed and finalized offline with Asil.</span>
              </div>
            </div>

            <div className="border-t border-white/5 pt-4 mb-6">
              <div className="flex justify-between items-center">
                <span className="text-base font-bold text-text-primary">Total Estimate</span>
                <span className="text-2xl font-extrabold text-text-primary text-glow-blue">
                  ₹{subtotal}
                </span>
              </div>
            </div>

            {/* Check for stale/disabled items before letting checkout */}
            {cartItems.some((i) => !i.is_available || i.needs_attention) ? (
              <div className="flex flex-col gap-3">
                <div className="p-3 bg-neon-pink/10 border border-neon-pink/20 rounded-md text-xs text-text-primary flex gap-2">
                  <AlertTriangle className="text-neon-pink flex-shrink-0" size={14} />
                  <span>Cannot checkout with inactive or outdated configuration items. Please resolve warnings.</span>
                </div>
                <button
                  disabled
                  className="w-full py-3.5 rounded-lg font-bold bg-white/10 text-white/40 flex items-center justify-center gap-2 cursor-not-allowed"
                >
                  Proceed to Checkout <ArrowRight size={16} />
                </button>
              </div>
            ) : (
              <Link
                href="/checkout"
                className="w-full py-3.5 px-6 rounded-lg font-bold bg-neon-blue text-[#0B0B0F] flex items-center justify-center gap-2 transition-all duration-300 transform hover:scale-[1.02] shadow-glow-blue hover:brightness-110"
              >
                Proceed to Checkout <ArrowRight size={16} />
              </Link>
            )}
          </div>
        </div>
      )}

      {/* RE-CONFIGURE MODAL (SIMULATED DYNAMIC SCHEMA RE-EDIT) */}
      {editingItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-void-black/80 backdrop-blur-md">
          <div className="w-full max-w-md rounded-xl glass-panel border border-neon-yellow shadow-glow-yellow p-6 relative">
            <h3 className="text-xl font-bold font-display text-text-primary text-glow-yellow mb-2 flex items-center gap-2">
              <RefreshCw size={18} className="animate-spin-slow text-neon-yellow" />
              Re-Configure Item
            </h3>
            <p className="text-xs text-text-muted mb-6 leading-relaxed">
              Adjust your custom options for <span className="font-semibold text-text-primary">&quot;{editingItem.product_title}&quot;</span> to resolve outdated schemas:
            </p>

            <div className="flex flex-col gap-4">
              {/* Option: Base Selection */}
              <div>
                <label className="text-xs font-bold text-text-primary uppercase tracking-wider block mb-2">Base / Color Type</label>
                <div className="flex gap-2">
                  {['Electric Pink', 'Electric Blue', 'Electric Violet'].map((col) => (
                    <button
                      key={col}
                      type="button"
                      onClick={() => setEditedAttributes(p => ({ ...p, color: col }))}
                      className={`flex-1 py-2 px-3 rounded-lg border text-xs font-bold transition-all ${
                        editedAttributes.color === col 
                          ? 'border-neon-violet bg-neon-violet/10 text-neon-violet shadow-glow-violet' 
                          : 'border-white/10 text-text-muted hover:border-white/20'
                      }`}
                    >
                      {col}
                    </button>
                  ))}
                </div>
              </div>

              {/* Option: Backing / Details */}
              <div>
                <label className="text-xs font-bold text-text-primary uppercase tracking-wider block mb-2">Engraving / Backing Option</label>
                <div className="flex gap-2">
                  {['cut_to_shape', 'whole_board'].map((cut) => (
                    <button
                      key={cut}
                      type="button"
                      onClick={() => setEditedAttributes(p => ({ ...p, backing: cut }))}
                      className={`flex-1 py-2 px-3 rounded-lg border text-xs font-bold transition-all ${
                        editedAttributes.backing === cut 
                          ? 'border-neon-violet bg-neon-violet/10 text-neon-violet shadow-glow-violet' 
                          : 'border-white/10 text-text-muted hover:border-white/20'
                      }`}
                    >
                      {cut === 'cut_to_shape' ? 'Contour Cut' : 'Full Board'}
                    </button>
                  ))}
                </div>
              </div>

              {/* Option: Size */}
              <div>
                <label className="text-xs font-bold text-text-primary uppercase tracking-wider block mb-2">Size selection</label>
                <select
                  value={(editedAttributes.size as string) || 'small'}
                  onChange={(e) => setEditedAttributes(p => ({ ...p, size: e.target.value }))}
                  className="w-full px-3 py-2 rounded-lg bg-surface-panel border border-white/10 text-xs text-text-primary"
                >
                  <option value="small">Small (2ft x 1ft)</option>
                  <option value="medium">Medium (3ft x 1.5ft)</option>
                  <option value="large">Large (4ft x 2ft)</option>
                </select>
              </div>
            </div>

            <div className="flex gap-4 mt-8 border-t border-white/5 pt-4">
              <button
                type="button"
                onClick={() => setEditingItem(null)}
                className="flex-1 py-2.5 rounded-lg border border-white/10 text-xs text-text-muted font-bold hover:bg-white/5 hover:text-text-primary transition-all"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleSaveReconfigured}
                className="flex-1 py-2.5 rounded-lg bg-neon-yellow text-[#0B0B0F] text-xs font-bold shadow-glow-yellow hover:brightness-110 transition-all flex items-center justify-center gap-1.5"
              >
                <CheckCircle2 size={14} /> Save Config
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
    </div>
  );
}

'use client';

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { api } from '@/lib/api';

export interface CartItem {
  id: string;
  name: string;
  thumbnail: string;
  quantity: number;
  configuration: Record<string, any>;
  price: number;
}

export interface CartSummary {
  subtotal: number;
  shipping: number;
  tax: number;
  total: number;
}

interface CartContextType {
  items: CartItem[];
  summary: CartSummary;
  loading: boolean;
  refreshCart: () => Promise<void>;
}

const CartContext = createContext<CartContextType | undefined>(undefined);

export function CartProvider({ children }: { children: React.ReactNode }) {
  const [items, setItems] = useState<CartItem[]>([]);
  const [summary, setSummary] = useState<CartSummary>({
    subtotal: 0,
    shipping: 0,
    tax: 0,
    total: 0,
  });
  const [loading, setLoading] = useState(true);

  const refreshCart = useCallback(async () => {
    try {
      const res = await api.get('/cart');
      const cartData = res.data || res;
      if (cartData && Array.isArray(cartData.items)) {
        const mappedItems = cartData.items.map((item: any) => ({
          id: item._id || item.id || item.product_id,
          name: item.product_title || 'Custom Configured Item',
          thumbnail: item.ai_preview_image || item.reference_image || '/placeholder-image.png',
          quantity: item.quantity || 1,
          configuration: item.selected_attributes || {},
          price: item.unit_price_estimate || item.line_total_estimate || 0,
        }));
        setItems(mappedItems);

        const subtotal = cartData.subtotal_estimate || 0;
        const shipping = 0; // free shipping
        const tax = 0;
        setSummary({
          subtotal,
          shipping,
          tax,
          total: subtotal + shipping + tax,
        });
      }
    } catch (err) {
      console.error('Error refreshing cart context:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshCart();
  }, [refreshCart]);

  return (
    <CartContext.Provider value={{ items, summary, loading, refreshCart }}>
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  const context = useContext(CartContext);
  
  // Local fallback if context is not present (i.e. not wrapped in provider)
  const [localItems, setLocalItems] = useState<CartItem[]>([]);
  const [localSummary, setLocalSummary] = useState<CartSummary>({
    subtotal: 0,
    shipping: 0,
    tax: 0,
    total: 0,
  });
  const [localLoading, setLocalLoading] = useState(true);

  const localRefresh = useCallback(async () => {
    try {
      const res = await api.get('/cart');
      const cartData = res.data || res;
      if (cartData && Array.isArray(cartData.items)) {
        const mappedItems = cartData.items.map((item: any) => ({
          id: item._id || item.id || item.product_id,
          name: item.product_title || 'Custom Configured Item',
          thumbnail: item.ai_preview_image || item.reference_image || '/placeholder-image.png',
          quantity: item.quantity || 1,
          configuration: item.selected_attributes || {},
          price: item.unit_price_estimate || item.line_total_estimate || 0,
        }));
        setLocalItems(mappedItems);

        const subtotal = cartData.subtotal_estimate || 0;
        const shipping = 0;
        const tax = 0;
        setLocalSummary({
          subtotal,
          shipping,
          tax,
          total: subtotal + shipping + tax,
        });
      }
    } catch (err) {
      console.error('Error in local useCart refresh:', err);
    } finally {
      setLocalLoading(false);
    }
  }, []);

  useEffect(() => {
    if (context === undefined) {
      localRefresh();
    }
  }, [context, localRefresh]);

  if (context !== undefined) {
    return context;
  }

  return {
    items: localItems,
    summary: localSummary,
    loading: localLoading,
    refreshCart: localRefresh,
  };
}

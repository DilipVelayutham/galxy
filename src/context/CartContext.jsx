import { createContext, useContext, useState, useEffect, useRef, useCallback } from 'react';
import { mockCartApi } from '../api/mockCartApi';

const CartContext = createContext();

const sanitizeCartData = (cartData) => {
  if (!cartData) return { items: [], item_count: 0, subtotal_estimate: 0 };
  const sanitizedItems = (cartData.items || []).map(item => {
    const unitPrice = isNaN(Number(item.unit_price_estimate)) || Number(item.unit_price_estimate) < 0 ? 0 : Number(item.unit_price_estimate);
    const lineTotal = isNaN(Number(item.line_total_estimate)) || Number(item.line_total_estimate) < 0 ? 0 : Number(item.line_total_estimate);
    return {
      ...item,
      unit_price_estimate: unitPrice,
      line_total_estimate: lineTotal
    };
  });
  const subtotal = isNaN(Number(cartData.subtotal_estimate)) || Number(cartData.subtotal_estimate) < 0 ? 0 : Number(cartData.subtotal_estimate);
  const count = isNaN(Number(cartData.item_count)) || Number(cartData.item_count) < 0 ? 0 : Number(cartData.item_count);
  return {
    ...cartData,
    items: sanitizedItems,
    item_count: count,
    subtotal_estimate: subtotal
  };
};

export function CartProvider({ children }) {
  const [cart, setCart] = useState({ items: [], item_count: 0, subtotal_estimate: 0 });
  const [loading, setLoading] = useState(true);
  const [mutatingItems, setMutatingItems] = useState([]);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [badgeAnimate, setBadgeAnimate] = useState(false);
  const [badgeGlow, setBadgeGlow] = useState(false);
  const [toasts, setToasts] = useState([]);

  // Ref to track timeouts for each item quantity change
  const debounceTimeouts = useRef({});

  const showToast = useCallback((message, type = 'success') => {
    const id = Date.now();
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 4000);
  }, []);

  const triggerBadgeAnimation = useCallback(() => {
    setBadgeAnimate(true);
    setBadgeGlow(true);
    setTimeout(() => setBadgeAnimate(false), 300);
    setTimeout(() => setBadgeGlow(false), 1000);
  }, []);

  // Fetch initial cart
  const refreshCart = useCallback(async (silent = false) => {
    if (!silent) setLoading(true);
    try {
      const res = await mockCartApi.getCart();
      setCart(sanitizeCartData(res.data));
    } catch (err) {
      console.error("Failed to load cart:", err);
      showToast("Failed to fetch cart. Please try again.", "error");
    } finally {
      if (!silent) setLoading(false);
    }
  }, [showToast]);

  useEffect(() => {
    const timer = setTimeout(() => {
      refreshCart();
    }, 0);
    return () => clearTimeout(timer);
  }, [refreshCart]);

  // Clear all pending timeouts on unmount
  useEffect(() => {
    return () => {
      // eslint-disable-next-line react-hooks/exhaustive-deps
      Object.values(debounceTimeouts.current).forEach(clearTimeout);
    };
  }, []);

  // Remove Item directly
  const removeItem = useCallback(async (itemId) => {
    setMutatingItems(prev => [...prev, itemId]);
    try {
      const res = await mockCartApi.removeItem(itemId);
      setCart(sanitizeCartData(res.data));
      triggerBadgeAnimation();
      showToast("Item removed from cart.", "info");
    } catch (err) {
      console.error("Failed to remove item:", err);
      showToast("Error removing item.", "error");
      refreshCart(true);
    } finally {
      setMutatingItems(prev => prev.filter(id => id !== itemId));
    }
  }, [refreshCart, triggerBadgeAnimation, showToast]);

  // Debounced Quantity Stepper Update
  const updateQuantity = useCallback((itemId, newQuantity) => {
    // If quantity is <= 0, remove the item directly
    if (newQuantity <= 0) {
      removeItem(itemId);
      return;
    }

    // 1. Optimistic Update of local state immediately for instant feedback
    setCart(prev => {
      const updatedItems = prev.items.map(item => {
        if (item._id === itemId) {
          const unitPrice = isNaN(Number(item.unit_price_estimate)) || Number(item.unit_price_estimate) < 0 ? 0 : Number(item.unit_price_estimate);
          return {
            ...item,
            quantity: newQuantity,
            unit_price_estimate: unitPrice,
            line_total_estimate: unitPrice * newQuantity
          };
        }
        return item;
      });

      // Recalculate item count & subtotal based on optimistic values
      let itemCount = 0;
      let subtotal = 0;
      updatedItems.forEach(item => {
        if (item.is_available) {
          itemCount += item.quantity;
          subtotal += item.line_total_estimate;
        }
      });

      return sanitizeCartData({
        items: updatedItems,
        item_count: itemCount,
        subtotal_estimate: subtotal
      });
    });

    // 2. Mark this item as mutating to show loading spinner / disable buttons
    setMutatingItems(prev => {
      if (!prev.includes(itemId)) {
        return [...prev, itemId];
      }
      return prev;
    });

    // 3. Clear existing debounce timeout for this item
    if (debounceTimeouts.current[itemId]) {
      clearTimeout(debounceTimeouts.current[itemId]);
    }

    // 4. Set new timeout to call mock API
    debounceTimeouts.current[itemId] = setTimeout(async () => {
      try {
        const res = await mockCartApi.updateItemQuantity(itemId, newQuantity);
        setCart(sanitizeCartData(res.data));
        triggerBadgeAnimation();
      } catch (err) {
        console.error("Failed to update item quantity:", err);
        showToast("Error updating item quantity.", "error");
        // Revert by fetching server state
        refreshCart(true);
      } finally {
        setMutatingItems(prev => prev.filter(id => id !== itemId));
        delete debounceTimeouts.current[itemId];
      }
    }, 500); // 500ms debounce
  }, [refreshCart, triggerBadgeAnimation, showToast, removeItem]);

  // Clear Cart
  const clearCart = useCallback(async () => {
    setLoading(true);
    try {
      const res = await mockCartApi.clearCart();
      setCart(sanitizeCartData(res.data));
      triggerBadgeAnimation();
      return true;
    } catch (err) {
      console.error("Failed to clear cart:", err);
      showToast("Error clearing cart.", "error");
      refreshCart(true);
      return false;
    } finally {
      setLoading(false);
    }
  }, [refreshCart, triggerBadgeAnimation, showToast]);

  // Add Item (for Shop Detail page integration)
  const addProductToCart = useCallback(async (product) => {
    setLoading(true);
    try {
      const res = await mockCartApi.addDemoItem(product);
      setCart(sanitizeCartData(res.data));
      triggerBadgeAnimation();
      showToast(`Added ${product.product_title} to cart!`, "success");
      setDrawerOpen(true); // Open slide out drawer automatically on add
    } catch (err) {
      console.error("Failed to add product to cart:", err);
      showToast("Error adding product.", "error");
    } finally {
      setLoading(false);
    }
  }, [triggerBadgeAnimation, showToast]);

  return (
    <CartContext.Provider value={{
      cart,
      loading,
      mutatingItems,
      drawerOpen,
      setDrawerOpen,
      badgeAnimate,
      badgeGlow,
      toasts,
      showToast,
      updateQuantity,
      removeItem,
      clearCart,
      addProductToCart,
      refreshCart
    }}>
      {children}
    </CartContext.Provider>
  );
}

// eslint-disable-next-line react-refresh/only-export-components
export function useCart() {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error("useCart must be used within a CartProvider");
  }
  return context;
}

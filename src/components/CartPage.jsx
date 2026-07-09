import { useState, useEffect, useRef } from 'react';
import { ShoppingBag, ArrowLeft, ArrowRight, CheckCircle, Shield, Truck, RefreshCw, X } from 'lucide-react';
import { useCart } from '../context/CartContext';
import CartItemRow from './CartItemRow';
import { mockCartApi } from '../api/mockCartApi';

const PRODUCT_OPTIONS_LOOKUP = {
  prod_supernova: {
    Finish: [
      { value: 'Matte Black', label: 'Matte Black', price_modifier: 0, available: true },
      { value: 'Brushed Steel', label: 'Brushed Steel', price_modifier: 0, available: true },
      { value: 'Brushed Brass', label: 'Brushed Brass', price_modifier: 30, available: false }
    ]
  },
  prod_nebula: {
    Shade: [
      { value: 'Clear Glass', label: 'Clear Glass', price_modifier: 0, available: true },
      { value: 'Frosted Glass', label: 'Frosted Glass', price_modifier: 10, available: true },
      { value: 'Smoked Glass', label: 'Smoked Glass', price_modifier: 25, available: false }
    ]
  },
  prod_comet: {
    Finish: [
      { value: 'Matte Black', label: 'Matte Black', price_modifier: 0, available: false },
      { value: 'Brushed Steel', label: 'Brushed Steel', price_modifier: 0, available: true }
    ]
  }
};

export default function CartPage({ onBackToShop }) {
  const {
    cart,
    loading,
    mutatingItems,
    updateQuantity,
    removeItem,
    clearCart,
    refreshCart,
    showToast
  } = useCart();

  const [checkoutStep, setCheckoutStep] = useState('cart'); // 'cart', 'processing', 'completed'
  const [orderNumber, setOrderNumber] = useState('');
  const [fixingItem, setFixingItem] = useState(null); // The item currently being configured
  const [fixedAttributeName, setFixedAttributeName] = useState('');
  const [fixedAttributeValue, setFixedAttributeValue] = useState('');
  const modalRef = useRef(null);

  const hasItems = cart.items && cart.items.length > 0;

  // Checkout handoff flow
  const handleCheckout = async () => {
    setCheckoutStep('processing');
    showToast("Initiating Module 8 Checkout Handoff...", "info");
    
    // Simulate payment / checkout process (Module 8 flow)
    setTimeout(async () => {
      try {
        // Clear local/UI cart state only after DELETE /api/cart/clear succeeds
        const success = await clearCart();
        if (success) {
          const generatedOrder = `GLX-${Math.floor(100000 + Math.random() * 900000)}`;
          setOrderNumber(generatedOrder);
          setCheckoutStep('completed');
          showToast("Checkout completed! Cart cleared.", "success");
        } else {
          setCheckoutStep('cart');
          showToast("Checkout handoff failed because cart could not be cleared.", "error");
        }
      } catch {
        setCheckoutStep('cart');
        showToast("Error during checkout handoff.", "error");
      }
    }, 2500);
  };

  // Close modal if fixingItem is no longer in cart or no longer needs attention (e.g. database was reset)
  useEffect(() => {
    if (fixingItem) {
      const stillInCart = cart.items.find(i => i._id === fixingItem._id);
      if (!stillInCart || !stillInCart.needs_attention) {
        const timer = setTimeout(() => {
          setFixingItem(null);
        }, 0);
        return () => clearTimeout(timer);
      }
    }
  }, [cart, fixingItem]);

  // Focus trap and ESC key listener for the "Fix Selection" Modal
  useEffect(() => {
    if (!fixingItem) return;

    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        setFixingItem(null);
        return;
      }
      if (e.key === 'Tab') {
        if (!modalRef.current) return;
        const focusableElements = modalRef.current.querySelectorAll(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        if (focusableElements.length === 0) return;
        
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        if (e.shiftKey) {
          if (document.activeElement === firstElement) {
            lastElement.focus();
            e.preventDefault();
          }
        } else {
          if (document.activeElement === lastElement) {
            firstElement.focus();
            e.preventDefault();
          }
        }
      }
    };

    const previousActiveElement = document.activeElement;
    document.addEventListener('keydown', handleKeyDown);

    // Focus the first focusable element
    const timer = setTimeout(() => {
      if (modalRef.current) {
        const focusableElements = modalRef.current.querySelectorAll(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        if (focusableElements.length > 0) {
          focusableElements[0].focus();
        }
      }
    }, 50);

    return () => {
      clearTimeout(timer);
      document.removeEventListener('keydown', handleKeyDown);
      if (previousActiveElement && typeof previousActiveElement.focus === 'function') {
        previousActiveElement.focus();
      }
    };
  }, [fixingItem]);

  // Open "Fix Selection" Modal
  const handleOpenFixModal = (item) => {
    setFixingItem(item);
    
    // Find conflicted attribute based on warning details defensively
    const errMsg = (item.error_message || '').toLowerCase();
    const conflictedAttr = item.selected_attributes.find(attr => 
      errMsg.includes(attr.name.toLowerCase()) || 
      errMsg.includes(attr.value.toLowerCase())
    ) || item.selected_attributes.find(a => a.name.toLowerCase() === 'finish') || item.selected_attributes[0];

    setFixedAttributeName(conflictedAttr.name);
    setFixedAttributeValue(conflictedAttr.value);
  };

  // Save the Fixed Configuration
  const handleSaveFix = async () => {
    if (!fixingItem) return;

    try {
      const options = PRODUCT_OPTIONS_LOOKUP[fixingItem.product_id]?.[fixedAttributeName] || [];
      const chosenOpt = options.find(o => o.value === fixedAttributeValue);
      const newModifier = chosenOpt ? chosenOpt.price_modifier : 0;

      // Create new selected attributes with the fixed value
      const updatedAttributes = fixingItem.selected_attributes.map(attr => {
        if (attr.name === fixedAttributeName) {
          return { ...attr, value: fixedAttributeValue, price_modifier: newModifier };
        }
        return attr;
      });

      // Recalculate unit price based on base price + modifiers
      const basePrice = fixingItem.base_price || 450;
      const totalModifiers = updatedAttributes.reduce((acc, a) => acc + (a.price_modifier || 0), 0);
      const newUnitPrice = basePrice + totalModifiers;

      // Call API abstraction instead of direct localStorage leakage
      await mockCartApi.updateItemConfiguration(fixingItem._id, updatedAttributes, newUnitPrice);

      // Refresh cart context
      await refreshCart(true);
      showToast("Configuration updated. Warning resolved!", "success");
      setFixingItem(null);
    } catch (err) {
      console.error(err);
      showToast("Failed to update configuration", "error");
    }
  };

  if (checkoutStep === 'processing') {
    return (
      <div className="min-h-[60vh] flex flex-col items-center justify-center text-center px-4 animate-fade-in">
        <div className="relative w-20 h-20 mb-6">
          <div className="absolute inset-0 border-4 border-accent-cyan/20 rounded-full"></div>
          <div className="absolute inset-0 border-4 border-accent-cyan border-t-transparent rounded-full animate-spin"></div>
          <ShoppingBag size={28} className="absolute inset-0 m-auto text-accent-cyan animate-pulse" />
        </div>
        <h2 className="text-xl sm:text-2xl font-bold tracking-tight mb-2">
          Processing Checkout Handoff
        </h2>
        <p className="text-sm text-text-secondary max-w-sm">
          Securing order details and passing cart items to Module 8: Checkout & Orders Flow. Please wait.
        </p>
      </div>
    );
  }

  if (checkoutStep === 'completed') {
    return (
      <div className="min-h-[60vh] flex flex-col items-center justify-center text-center px-4 animate-fade-in">
        <div className="w-16 h-16 rounded-full bg-accent-green/10 border border-accent-green/30 flex items-center justify-center text-accent-green mb-6 shadow-[0_0_20px_rgba(16,185,129,0.15)]">
          <CheckCircle size={32} />
        </div>
        <h2 className="text-2xl sm:text-3xl font-bold tracking-tight mb-2">
          Checkout Initiated!
        </h2>
        <p className="text-sm text-accent-green font-semibold mb-4">
          Order Number: {orderNumber}
        </p>
        <p className="text-sm text-text-secondary max-w-md mb-8">
          The cart has been successfully cleared on the server. Your customized configuration is now registered in the checkout system.
        </p>
        <button
          onClick={() => {
            setCheckoutStep('cart');
            onBackToShop();
          }}
          className="btn-primary"
        >
          <ArrowLeft size={16} />
          Return to Studio
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 animate-fade-in">
      {/* Back Button */}
      <button 
        onClick={onBackToShop}
        className="flex items-center gap-2 text-text-secondary hover:text-text-primary mb-6 transition-colors text-sm"
      >
        <ArrowLeft size={16} />
        Continue Customizing
      </button>

      {/* Title */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">Shopping Cart</h1>
          <p className="text-sm text-text-secondary mt-1">
            Review your custom lighting specs and hand off to checkout.
          </p>
        </div>
        
        {hasItems && (
          <button
            onClick={() => refreshCart(false)}
            className="flex items-center gap-1.5 text-xs text-text-secondary hover:text-accent-cyan transition-colors self-start sm:self-auto"
          >
            <RefreshCw size={13} className={loading ? 'animate-spin' : ''} />
            Refresh Quotes
          </button>
        )}
      </div>

      {loading && !fixingItem ? (
        <div className="min-h-[40vh] flex flex-col items-center justify-center text-text-secondary">
          <div className="w-10 h-10 border-2 border-accent-cyan border-t-transparent rounded-full animate-spin mb-4"></div>
          <p className="text-sm">Recalculating custom dimensions...</p>
        </div>
      ) : !hasItems ? (
        <div className="glass-panel rounded-2xl p-12 text-center border border-white/5 flex flex-col items-center justify-center min-h-[40vh]">
          <div className="w-16 h-16 rounded-full bg-white/[0.02] border border-white/5 flex items-center justify-center text-text-muted mb-4">
            <ShoppingBag size={28} />
          </div>
          <h3 className="text-xl font-semibold text-text-primary">Your cart is empty</h3>
          <p className="text-sm text-text-secondary max-w-sm mt-2">
            You don't have any customized items in your cart. Head back to the Product Configurator to design your custom fixtures.
          </p>
          <button
            onClick={onBackToShop}
            className="btn-primary mt-6 text-sm"
          >
            Design Custom Lights
            <ArrowRight size={16} />
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
          
          {/* Cart Items list */}
          <div className="lg:col-span-2">
            {cart.items.map(item => (
              <CartItemRow
                key={item._id}
                item={item}
                isMutating={mutatingItems.includes(item._id)}
                onUpdateQty={updateQuantity}
                onRemove={removeItem}
                onFixSelection={handleOpenFixModal}
              />
            ))}
          </div>

          {/* Checkout Summary Card */}
          <div className="glass-panel rounded-2xl p-6 border border-white/5 lg:sticky lg:top-8">
            <h3 className="text-lg font-bold border-b border-white/5 pb-4 mb-4">
              Quote Summary
            </h3>
            
            <div className="space-y-3.5 mb-6 text-sm">
              <div className="flex justify-between text-text-secondary">
                <span>Configured Items</span>
                <span>{cart.item_count}</span>
              </div>
              <div className="flex justify-between text-text-secondary">
                <span>Production Lead Time</span>
                <span className="text-accent-pink">4-6 Weeks</span>
              </div>
              <div className="flex justify-between text-text-secondary">
                <span>Shipping</span>
                <span className="text-text-primary font-medium">Free Express</span>
              </div>
              
              <div className="border-t border-white/5 pt-4 mt-4 flex justify-between items-end">
                <div>
                  <span className="text-base font-bold text-text-primary block">Subtotal Estimate</span>
                  <span className="text-[10px] text-text-muted leading-none">Includes materials & configurator surcharges</span>
                </div>
                <span className="text-2xl font-bold text-accent-cyan glow-text-cyan">
                  ${cart.subtotal_estimate}
                </span>
              </div>
            </div>

            {/* Checkout Action Button */}
            <button
              onClick={handleCheckout}
              disabled={cart.items.some(item => !item.is_available)}
              className="btn-primary w-full justify-center py-3.5 mb-4 text-sm font-semibold tracking-wide"
            >
              Proceed to Checkout
              <ArrowRight size={16} />
            </button>

            {/* If there are unavailable items, warn the user */}
            {cart.items.some(item => !item.is_available) && (
              <div className="text-xs text-red-400 bg-red-500/10 border border-red-500/20 p-3 rounded-lg text-center mb-4">
                Please remove sold out items before proceeding to checkout.
              </div>
            )}

            <div className="space-y-3 text-xs text-text-secondary border-t border-white/5 pt-4">
              <div className="flex items-center gap-2">
                <Truck size={14} className="text-accent-cyan" />
                <span>Fully insured premium freight shipping</span>
              </div>
              <div className="flex items-center gap-2">
                <Shield size={14} className="text-accent-cyan" />
                <span>100% Secure handoff to Module 8 Checkout</span>
              </div>
            </div>
          </div>

        </div>
      )}

      {/* Fix Selection Modal */}
      {fixingItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 animate-fade-in">
          {/* Overlay */}
          <div className="absolute inset-0 bg-black/75 backdrop-blur-sm" onClick={() => setFixingItem(null)} />
          
          {/* Modal Content */}
          <div 
            ref={modalRef}
            role="dialog"
            aria-modal="true"
            aria-labelledby="fix-modal-title"
            aria-describedby="fix-modal-desc"
            className="relative w-full max-w-md glass-panel border border-white/10 rounded-2xl p-6 shadow-2xl z-10 animate-scale-up"
          >
            <button 
              onClick={() => setFixingItem(null)}
              className="absolute top-4 right-4 text-text-secondary hover:text-text-primary focus:outline-none focus:ring-2 focus:ring-accent-cyan rounded-md p-1"
              aria-label="Close modal"
            >
              <X size={18} />
            </button>

            <h3 id="fix-modal-title" className="text-lg font-bold mb-1">Fix Product Configuration</h3>
            <p id="fix-modal-desc" className="text-xs text-text-secondary mb-4">
              Resolve configuration error for <strong className="text-text-primary">{fixingItem.product_title}</strong>
            </p>

            {/* Error Message */}
            <div className="bg-amber-500/10 border border-amber-500/20 text-amber-400 p-3 rounded-lg text-xs mb-5">
              <span className="font-semibold block mb-0.5">Backend Error Response:</span>
              {fixingItem.error_message}
            </div>

            {/* Reconfigurator Input */}
            <div className="space-y-4 mb-6">
              <label className="text-xs font-semibold text-text-secondary block">
                Select Alternative {fixedAttributeName}:
              </label>
              
              <div className="grid grid-cols-2 gap-3">
                {(PRODUCT_OPTIONS_LOOKUP[fixingItem.product_id]?.[fixedAttributeName] || []).map(opt => (
                  <button
                    key={opt.value}
                    disabled={!opt.available}
                    onClick={() => setFixedAttributeValue(opt.value)}
                    className={`p-3 rounded-xl border text-xs text-left flex flex-col justify-between h-20 transition-all ${
                      fixedAttributeValue === opt.value
                        ? 'border-accent-cyan bg-accent-cyan/10 text-text-primary'
                        : opt.available
                          ? 'border-white/5 bg-white/[0.02] text-text-secondary hover:border-white/20'
                          : 'border-red-500/10 bg-black/40 text-text-muted cursor-not-allowed opacity-50'
                    }`}
                  >
                    <span className="font-semibold">{opt.label}</span>
                    <span className="text-[10px] text-text-muted">
                      {opt.available ? (opt.price_modifier > 0 ? `+$${opt.price_modifier}` : 'Included') : 'Not Available'}
                    </span>
                  </button>
                ))}
              </div>
            </div>

            {/* Modal Actions */}
            <div className="flex gap-3 justify-end border-t border-white/5 pt-4">
              <button
                onClick={() => setFixingItem(null)}
                className="btn-secondary text-xs px-4 py-2"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveFix}
                disabled={!fixedAttributeValue}
                className="btn-primary text-xs px-5 py-2"
              >
                Apply Correction
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

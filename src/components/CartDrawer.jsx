import { X, ShoppingBag, ArrowRight } from 'lucide-react';
import { useCart } from '../context/CartContext';
import CartItemRow from './CartItemRow';

export default function CartDrawer({ onViewCartPage, onProceedCheckout }) {
  const { 
    cart, 
    loading, 
    mutatingItems, 
    drawerOpen, 
    setDrawerOpen, 
    updateQuantity, 
    removeItem 
  } = useCart();

  if (!drawerOpen) return null;

  const hasItems = cart.items && cart.items.length > 0;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden animate-fade-in">
      {/* Dark Overlay Background */}
      <div 
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={() => setDrawerOpen(false)}
      />

      <div className="absolute inset-y-0 right-0 max-w-full flex pl-10">
        {/* Sliding Panel */}
        <div className="w-screen max-w-md glass-panel border-l border-white/10 flex flex-col animate-slide-in">
          
          {/* Header */}
          <div className="p-5 border-b border-white/5 flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <ShoppingBag size={20} className="text-accent-cyan" />
              <h2 className="text-lg font-bold tracking-tight">Shopping Drawer</h2>
              <span className="bg-accent-cyan/15 text-accent-cyan text-xs font-semibold px-2 py-0.5 rounded-full border border-accent-cyan/20">
                {cart.item_count} {cart.item_count === 1 ? 'item' : 'items'}
              </span>
            </div>
            <button 
              onClick={() => setDrawerOpen(false)}
              className="p-1.5 rounded-lg hover:bg-white/5 text-text-secondary hover:text-text-primary transition-all"
            >
              <X size={20} />
            </button>
          </div>

          {/* Cart Items List */}
          <div className="flex-1 overflow-y-auto p-5">
            {loading ? (
              <div className="h-full flex flex-col items-center justify-center text-text-secondary">
                <div className="w-8 h-8 border-2 border-accent-cyan border-t-transparent rounded-full animate-spin mb-3"></div>
                <p className="text-sm">Fetching items...</p>
              </div>
            ) : !hasItems ? (
              <div className="h-full flex flex-col items-center justify-center text-center">
                <div className="w-16 h-16 rounded-full bg-white/[0.02] border border-white/5 flex items-center justify-center text-text-muted mb-4">
                  <ShoppingBag size={28} />
                </div>
                <h3 className="text-base font-semibold text-text-primary">Your cart is empty</h3>
                <p className="text-xs text-text-secondary max-w-xs mt-1">
                  Explore GALXY lighting configurations to find the perfect addition for your space.
                </p>
                <button
                  onClick={() => setDrawerOpen(false)}
                  className="btn-secondary text-xs mt-5"
                >
                  Start Customizing
                </button>
              </div>
            ) : (
              <div className="space-y-1">
                {cart.items.map(item => (
                  <CartItemRow
                    key={item._id}
                    item={item}
                    layout="compact"
                    isMutating={mutatingItems.includes(item._id)}
                    onUpdateQty={updateQuantity}
                    onRemove={removeItem}
                  />
                ))}
              </div>
            )}
          </div>

          {/* Drawer Footer Summary */}
          {hasItems && !loading && (
            <div className="p-5 border-t border-white/5 bg-black/30">
              <div className="flex justify-between items-center mb-4">
                <span className="text-sm text-text-secondary font-medium">Subtotal Estimate</span>
                <span className="text-xl font-bold text-accent-cyan glow-text-cyan">
                  ${cart.subtotal_estimate}
                </span>
              </div>
              
              <p className="text-[10px] text-text-muted mb-4 text-center leading-relaxed">
                * Prices dynamically sourced from the Pricing Engine API, inclusive of custom material options and surcharges.
              </p>

              <div className="grid grid-cols-2 gap-3">
                <button
                  onClick={() => {
                    setDrawerOpen(false);
                    onViewCartPage();
                  }}
                  className="btn-secondary justify-center text-xs py-3"
                >
                  View Full Cart
                </button>
                <button
                  onClick={() => {
                    setDrawerOpen(false);
                    onProceedCheckout();
                  }}
                  className="btn-primary justify-center text-xs py-3"
                >
                  Checkout
                  <ArrowRight size={14} />
                </button>
              </div>
            </div>
          )}

        </div>
      </div>
    </div>
  );
}

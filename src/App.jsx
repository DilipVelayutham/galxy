import { useState } from 'react';
import { CartProvider, useCart } from './context/CartContext';
import ProductDemo from './components/ProductDemo';
import CartPage from './components/CartPage';
import CartDrawer from './components/CartDrawer';
import ControlPanel from './components/ControlPanel';
import { ShoppingBag, Sparkles, AlertCircle, CheckCircle2, Info } from 'lucide-react';

function AppContent() {
  const [view, setView] = useState('shop'); // 'shop' or 'cart'
  const { 
    cart, 
    setDrawerOpen, 
    badgeAnimate, 
    badgeGlow, 
    toasts 
  } = useCart();

  return (
    <div className="min-h-screen bg-bg-primary text-text-primary flex flex-col relative select-none">
      
      {/* Premium Header/Navigation */}
      <header className="sticky top-0 z-40 border-b border-white/5 bg-bg-primary/80 backdrop-blur-md">
        <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
          {/* Logo */}
          <div 
            onClick={() => setView('shop')}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                setView('shop');
                e.preventDefault();
              }
            }}
            tabIndex={0}
            role="button"
            aria-label="GALXY Custom Studio Configurator Homepage"
            className="flex items-center gap-2 cursor-pointer group focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-cyan rounded-lg p-1"
          >
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-accent-purple to-accent-cyan flex items-center justify-center shadow-lg group-hover:scale-105 transition-all">
              <Sparkles size={16} className="text-black" />
            </div>
            <div>
              <span className="font-extrabold tracking-widest text-lg bg-gradient-to-r from-text-primary via-accent-cyan to-accent-pink bg-clip-text text-transparent">
                GALXY
              </span>
              <span className="text-[10px] text-text-muted font-semibold tracking-wider block -mt-1 uppercase">
                Custom Studio
              </span>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="flex items-center gap-6">
            <button 
              onClick={() => setView('shop')}
              className={`text-sm font-semibold tracking-wide transition-colors ${
                view === 'shop' ? 'text-accent-cyan glow-text-cyan' : 'text-text-secondary hover:text-text-primary'
              }`}
            >
              Configurator
            </button>
            <button 
              onClick={() => setView('cart')}
              className={`text-sm font-semibold tracking-wide transition-colors ${
                view === 'cart' ? 'text-accent-cyan glow-text-cyan' : 'text-text-secondary hover:text-text-primary'
              }`}
            >
              Cart page
            </button>

            {/* Shopping Cart Icon Trigger */}
            <button
              onClick={() => setDrawerOpen(true)}
              className="relative p-2 hover:bg-white/5 rounded-xl border border-white/0 hover:border-white/5 transition-all flex items-center justify-center group"
              aria-label="Open cart drawer"
            >
              <ShoppingBag 
                size={20} 
                className={`text-text-primary group-hover:text-accent-cyan transition-colors ${
                  badgeGlow ? 'text-accent-cyan animate-pulse-glow' : ''
                }`} 
              />
              
              {/* Live Badge showing count */}
              {cart.item_count > 0 && (
                <span className={`absolute -top-1.5 -right-1.5 min-w-5 h-5 px-1.5 flex items-center justify-center rounded-full bg-accent-cyan text-black font-extrabold text-[10px] border-2 border-bg-primary transition-all duration-300 shadow-[0_0_10px_rgba(0,242,254,0.4)] ${
                  badgeAnimate ? 'animate-bounce-scale' : ''
                }`}>
                  {cart.item_count}
                </span>
              )}
            </button>
          </nav>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-grow py-8 relative">
        {view === 'shop' ? (
          <ProductDemo />
        ) : (
          <CartPage onBackToShop={() => setView('shop')} />
        )}
      </main>

      {/* Footer */}
      <footer className="py-6 border-t border-white/5 text-center text-xs text-text-muted bg-black/10">
        <p>© 2026 GALXY Custom Lighting & Craft Studio. All rights reserved.</p>
        <p className="text-[10px] text-text-muted mt-1 opacity-70">
          Module 6 Frontend cart UI • Dhanush Lead (Frontend)
        </p>
      </footer>

      {/* Slide-out Drawer */}
      <CartDrawer 
        onViewCartPage={() => setView('cart')}
        onProceedCheckout={() => setView('cart')}
      />

      {/* Interactive Simulation Panel */}
      <ControlPanel />

      {/* Toasts Stack */}
      <div className="fixed top-6 right-6 z-50 flex flex-col gap-2.5 max-w-sm pointer-events-none">
        {toasts.map(toast => (
          <div 
            key={toast.id}
            className={`pointer-events-auto p-4 rounded-xl shadow-2xl glass-panel border flex items-start gap-3 animate-slide-in ${
              toast.type === 'success' 
                ? 'border-accent-green/30 text-accent-green' 
                : toast.type === 'error'
                  ? 'border-accent-red/30 text-accent-red'
                  : 'border-accent-cyan/30 text-accent-cyan'
            }`}
          >
            {toast.type === 'success' && <CheckCircle2 size={16} className="mt-0.5 flex-shrink-0" />}
            {toast.type === 'error' && <AlertCircle size={16} className="mt-0.5 flex-shrink-0" />}
            {toast.type === 'info' && <Info size={16} className="mt-0.5 flex-shrink-0" />}
            
            <span className="text-xs font-semibold text-text-primary">
              {toast.message}
            </span>
          </div>
        ))}
      </div>

    </div>
  );
}

export default function App() {
  return (
    <CartProvider>
      <AppContent />
    </CartProvider>
  );
}

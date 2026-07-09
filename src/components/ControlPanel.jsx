import { useState, useEffect } from 'react';
import { Settings, RefreshCw, Clock, AlertTriangle } from 'lucide-react';
import { mockCartApi } from '../api/mockCartApi';
import { useCart } from '../context/CartContext';

export default function ControlPanel() {
  const { cart, refreshCart, showToast } = useCart();
  const [isOpen, setIsOpen] = useState(false);
  const [latency, setLatency] = useState(() => mockCartApi.getLatency());
  const [staleStates, setStaleStates] = useState(() => mockCartApi.getStaleStates());

  // Sync state values on load asynchronously to avoid cascading synchronous render
  useEffect(() => {
    const timer = setTimeout(() => {
      setLatency(mockCartApi.getLatency());
      setStaleStates(mockCartApi.getStaleStates());
    }, 0);
    return () => clearTimeout(timer);
  }, [cart]);

  const handleLatencyChange = (e) => {
    const val = parseInt(e.target.value) || 0;
    setLatency(val);
    mockCartApi.setLatency(val);
  };

  const toggleStaleState = async (itemId, type) => {
    const currentState = staleStates[itemId] || { is_available: true, needs_attention: false, error_message: '' };
    
    let updated;
    if (type === 'available') {
      updated = {
        ...currentState,
        is_available: !currentState.is_available
      };
    } else if (type === 'attention') {
      const isActivating = !currentState.needs_attention;
      const targetItem = cart.items.find(i => i._id === itemId);
      let error_message = '';
      if (isActivating && targetItem) {
        if (targetItem.product_id === 'prod_supernova') {
          error_message = 'Brushed Brass finish is currently unavailable. Please select Matte Black or Brushed Steel.';
        } else if (targetItem.product_id === 'prod_nebula') {
          error_message = 'Smoked Glass shade is currently unavailable. Please select Clear Glass or Frosted Glass.';
        } else if (targetItem.product_id === 'prod_comet') {
          error_message = 'Matte Black finish is currently unavailable. Please select Brushed Steel.';
        } else {
          error_message = 'This configuration is out of stock. Please select another option.';
        }
      }
      updated = {
        ...currentState,
        needs_attention: isActivating,
        error_message
      };
    }

    if (!updated) return;

    // Save to mock database
    mockCartApi.setStaleState(itemId, updated);
    setStaleStates(prev => ({
      ...prev,
      [itemId]: updated
    }));

    // Trigger cart state refresh in context
    await refreshCart(true);
    showToast(`Simulation state updated for item.`, "info");
  };

  const handleReset = async () => {
    mockCartApi.resetCart();
    setLatency(400);
    setStaleStates({});
    await refreshCart(false);
    showToast("Simulated database has been reset.", "success");
  };

  return (
    <div className={`fixed bottom-4 left-4 z-50 transition-all duration-300 font-sans ${isOpen ? 'w-80' : 'w-12'}`}>
      {/* Floating Toggle Button */}
      {!isOpen ? (
        <button
          onClick={() => setIsOpen(true)}
          className="w-12 h-12 rounded-full bg-accent-purple text-text-primary border border-accent-purple/30 flex items-center justify-center shadow-lg hover:shadow-purple-500/20 hover:scale-105 transition-all"
          title="Open Developer Control Panel"
        >
          <Settings size={20} className="animate-spin-slow" />
        </button>
      ) : (
        /* Floating Card */
        <div className="glass-panel border border-accent-purple/30 rounded-2xl p-5 shadow-2xl bg-black/85 backdrop-blur-md animate-scale-up">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-white/10 pb-3 mb-4">
            <div className="flex items-center gap-2 text-accent-purple">
              <Settings size={18} />
              <h3 className="text-sm font-bold tracking-wide uppercase">Simulation Console</h3>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="text-xs text-text-muted hover:text-text-primary uppercase font-bold"
            >
              Hide
            </button>
          </div>

          <p className="text-[11px] text-text-secondary leading-relaxed mb-4">
            Toggle state variables here to verify Module 6's frontend response to dynamic/stale backend records.
          </p>

          {/* Section: API Latency */}
          <div className="mb-4 p-3 bg-white/[0.02] border border-white/5 rounded-xl">
            <div className="flex items-center justify-between text-xs text-text-secondary mb-2">
              <span className="flex items-center gap-1">
                <Clock size={13} className="text-accent-cyan" />
                Mock API Latency
              </span>
              <span className="font-semibold text-accent-cyan">{latency}ms</span>
            </div>
            <input
              type="range"
              min="0"
              max="2500"
              step="100"
              value={latency}
              onChange={handleLatencyChange}
              className="w-full accent-accent-cyan h-1 bg-tertiary rounded-lg appearance-none cursor-pointer"
            />
          </div>

          {/* Section: Stale States */}
          <div className="mb-4">
            <div className="text-xs font-semibold text-text-secondary mb-2 flex items-center gap-1">
              <AlertTriangle size={13} className="text-accent-amber" />
              Dynamic Cart Stale States
            </div>
            
            {cart.items.length === 0 ? (
              <div className="text-[11px] text-text-muted py-2 text-center">
                Add items to cart to simulate stale states.
              </div>
            ) : (
              <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                {cart.items.map(item => {
                  const state = staleStates[item._id] || { is_available: true, needs_attention: false };
                  return (
                    <div key={item._id} className="p-2.5 bg-tertiary/60 border border-white/5 rounded-lg text-xs">
                      <div className="font-medium text-text-primary truncate mb-2">
                        {item.product_title}
                      </div>
                      
                      <div className="grid grid-cols-2 gap-2">
                        {/* Availability Toggle */}
                        <button
                          onClick={() => toggleStaleState(item._id, 'available')}
                          className={`px-2 py-1.5 rounded-md font-semibold text-[10px] text-center border transition-all ${
                            !state.is_available
                              ? 'bg-red-500/20 border-red-500/30 text-red-300'
                              : 'bg-white/[0.02] border-white/5 text-text-secondary hover:border-white/10'
                          }`}
                        >
                          {!state.is_available ? 'Sold Out' : 'Make Sold Out'}
                        </button>

                        {/* Attention Toggle */}
                        <button
                          onClick={() => toggleStaleState(item._id, 'attention')}
                          className={`px-2 py-1.5 rounded-md font-semibold text-[10px] text-center border transition-all ${
                            state.needs_attention
                              ? 'bg-amber-500/20 border-amber-500/30 text-amber-300'
                              : 'bg-white/[0.02] border-white/5 text-text-secondary hover:border-white/10'
                          }`}
                        >
                          {state.needs_attention ? 'Needs Attention' : 'Trigger Error'}
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Reset Action */}
          <button
            onClick={handleReset}
            className="w-full flex items-center justify-center gap-1.5 bg-white/[0.04] hover:bg-white/[0.08] text-xs font-semibold py-2.5 rounded-xl border border-white/10 text-text-secondary hover:text-text-primary transition-all mt-4"
          >
            <RefreshCw size={13} />
            Reset Simulated DB
          </button>
        </div>
      )}
    </div>
  );
}

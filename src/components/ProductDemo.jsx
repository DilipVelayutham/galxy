import { useState } from 'react';
import { useCart } from '../context/CartContext';
import { ShoppingBag, Sparkles, Check } from 'lucide-react';

export default function ProductDemo() {
  const { addProductToCart, loading } = useCart();
  
  // Configurator states
  const [selectedFinish, setSelectedFinish] = useState('Brushed Brass');
  const [selectedSize, setSelectedSize] = useState('Large (24")');
  const [customText, setCustomText] = useState('');

  // Dynamic price calculation matching spec derived on each render
  const basePrice = 450;
  const finishMod = selectedFinish === 'Brushed Brass' ? 30 : 0;
  const sizeMod = selectedSize === 'Large (24")' ? 50 : 0;
  const computedUnitPrice = basePrice + finishMod + sizeMod;

  const handleAddToCart = () => {
    const selectedAttributes = [
      { name: "Size", value: selectedSize, price_modifier: selectedSize === 'Large (24")' ? 50 : 0 },
      { name: "Finish", value: selectedFinish, price_modifier: selectedFinish === 'Brushed Brass' ? 30 : 0 },
      { name: "Bulb Type", value: "Edison LED (Warm)", price_modifier: 10 }
    ];

    const productSnapshot = {
      product_id: "prod_supernova",
      product_title: "Supernova Pendant Light",
      category_name: "Pendant Lights",
      thumbnail: "https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?w=150&auto=format&fit=crop&q=80",
      selected_attributes: selectedAttributes,
      custom_text: customText.trim() || null,
      base_price: 450,
      unit_price_estimate: computedUnitPrice + 10, // includes bulb modifier
    };

    addProductToCart(productSnapshot);
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 animate-fade-in">
      <div className="glass-panel rounded-2xl overflow-hidden border border-white/5 shadow-2xl grid grid-cols-1 md:grid-cols-2">
        {/* Left Side: Media Gallery */}
        <div className="relative bg-tertiary/40 border-r border-white/5 min-h-[300px] flex items-center justify-center p-6">
          <img 
            src="https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?w=500&auto=format&fit=crop&q=80" 
            alt="Supernova Pendant Light"
            className="max-h-[350px] w-full object-cover rounded-xl shadow-2xl border border-white/5 transition-transform hover:scale-102 duration-500"
          />
          <div className="absolute top-4 left-4 bg-accent-purple/20 text-accent-purple border border-accent-purple/30 text-[10px] font-bold tracking-widest px-2.5 py-1 rounded-full uppercase flex items-center gap-1">
            <Sparkles size={10} />
            Configurable Fixture
          </div>
        </div>

        {/* Right Side: Configurator Details */}
        <div className="p-6 sm:p-8 flex flex-col justify-between">
          <div>
            <span className="text-xs font-bold text-accent-pink tracking-widest uppercase">
              GALXY Craft Studio • Module 3/4 Mockup
            </span>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight mt-1.5 mb-2">
              Supernova Pendant Light
            </h1>
            <p className="text-sm text-text-secondary leading-relaxed mb-6">
              A striking celestial-inspired focal piece. Individually glassblown and hand-assembled with solid metal sockets. Customized variables automatically update production quotes.
            </p>

            {/* Configurator Attributes */}
            <div className="space-y-5">
              {/* Attribute 1: Finish */}
              <div>
                <label className="text-xs font-bold uppercase tracking-wider text-text-secondary block mb-2">
                  Metal Finish
                </label>
                <div className="flex gap-2.5">
                  {['Brushed Brass', 'Matte Black', 'Brushed Steel'].map(finish => (
                    <button
                      key={finish}
                      onClick={() => setSelectedFinish(finish)}
                      className={`relative px-3.5 py-2 rounded-lg text-xs font-semibold border flex items-center gap-1.5 transition-all ${
                        selectedFinish === finish
                          ? 'border-accent-cyan bg-accent-cyan/15 text-text-primary'
                          : 'border-white/5 bg-white/[0.02] text-text-secondary hover:border-white/10'
                      }`}
                    >
                      {selectedFinish === finish && <Check size={12} className="text-accent-cyan" />}
                      {finish}
                      <span className="text-[10px] text-text-muted">
                        {finish === 'Brushed Brass' ? '(+$30)' : ''}
                      </span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Attribute 2: Size */}
              <div>
                <label className="text-xs font-bold uppercase tracking-wider text-text-secondary block mb-2">
                  Fixture Size
                </label>
                <div className="flex gap-2.5">
                  {['Standard (16")', 'Large (24")'].map(size => (
                    <button
                      key={size}
                      onClick={() => setSelectedSize(size)}
                      className={`relative px-3.5 py-2 rounded-lg text-xs font-semibold border flex items-center gap-1.5 transition-all ${
                        selectedSize === size
                          ? 'border-accent-cyan bg-accent-cyan/15 text-text-primary'
                          : 'border-white/5 bg-white/[0.02] text-text-secondary hover:border-white/10'
                      }`}
                    >
                      {selectedSize === size && <Check size={12} className="text-accent-cyan" />}
                      {size}
                      <span className="text-[10px] text-text-muted">
                        {size === 'Large (24")' ? '(+$50)' : ''}
                      </span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Attribute 3: Custom Inscription */}
              <div>
                <label className="text-xs font-bold uppercase tracking-wider text-text-secondary block mb-2">
                  Custom Request (Optional)
                </label>
                <textarea
                  value={customText}
                  onChange={(e) => setCustomText(e.target.value)}
                  placeholder="e.g. Cord adjustments, installation ceiling height, special engravings..."
                  className="w-full text-xs bg-tertiary border border-white/5 hover:border-white/10 focus:border-accent-cyan/40 focus:ring-0 rounded-xl p-3 text-text-primary outline-none transition-all resize-none h-16"
                  maxLength={150}
                />
              </div>
            </div>
          </div>

          {/* Pricing & Add Action Panel */}
          <div className="mt-8 pt-6 border-t border-white/5">
            <div className="flex justify-between items-center mb-5">
              <div>
                <span className="text-[10px] font-bold text-text-secondary uppercase block">
                  Interactive Unit Quote
                </span>
                <span className="text-xs text-text-muted">Includes Warm LED Bulb (+$10)</span>
              </div>
              <div className="text-2xl sm:text-3xl font-extrabold text-accent-cyan glow-text-cyan">
                ${computedUnitPrice + 10}
              </div>
            </div>

            <button
              onClick={handleAddToCart}
              disabled={loading}
              className="btn-primary w-full justify-center py-3.5 font-bold tracking-wider"
            >
              <ShoppingBag size={18} />
              Add Configured Spec To Cart
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

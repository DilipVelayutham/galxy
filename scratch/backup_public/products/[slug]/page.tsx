'use client';

import React, { useState, use } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../../../../context/AuthContext';
import AttributeRenderer, { AttributeSchema } from '../../../../components/configurator/AttributeRenderer';
import { Sparkles, Plus, Minus, ShoppingCart, ShieldAlert, ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import Header from '../../../../components/Header';

// Mock product category attribute schema (matches schema in docs)
const mockNeonSchema: AttributeSchema[] = [
  {
    key: 'font',
    label: 'Font Style',
    type: 'select',
    required: true,
    options: [
      { value: 'cursive', label: 'Cursive Font', price_delta: 150 },
      { value: 'bold', label: 'Bold Modern Font', price_delta: 250 },
      { value: 'trigger_invalid_attribute', label: 'Deprecated Font (Triggers 400)', price_delta: 0 }
    ]
  },
  {
    key: 'color',
    label: 'Neon Glow Color',
    type: 'color_swatch',
    required: true,
    options: [
      { value: 'Electric Pink', label: 'Electric Pink Swatch', price_delta: 0, color_code: '#FF2E8A' },
      { value: 'Electric Blue', label: 'Electric Blue Swatch', price_delta: 0, color_code: '#18E7FF' },
      { value: 'Electric Violet', label: 'Electric Violet Swatch', price_delta: 150, color_code: '#9B5CFF' },
      { value: 'Electric Yellow', label: 'Electric Yellow Swatch', price_delta: 150, color_code: '#FFD84D' }
    ]
  },
  {
    key: 'backing',
    label: 'Acrylic Backing Cut',
    type: 'toggle',
    required: true,
    options: [
      { value: 'cut_to_shape', label: 'Contour Cut', price_delta: 0 },
      { value: 'whole_board', label: 'Full Board', price_delta: 200 }
    ]
  },
  {
    key: 'size',
    label: 'Overall Dimensions',
    type: 'image_swatch',
    required: true,
    options: [
      { 
        value: 'small', 
        label: 'Small (2ft x 1ft)', 
        price_delta: 0,
        preview_image: 'https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&q=80&w=200'
      },
      { 
        value: 'medium', 
        label: 'Medium (3ft x 1.5ft)', 
        price_delta: 450,
        preview_image: 'https://images.unsplash.com/photo-1507508064433-641572e9c133?auto=format&fit=crop&q=80&w=200'
      },
      { 
        value: 'large', 
        label: 'Large (4ft x 2ft)', 
        price_delta: 899,
        preview_image: 'https://images.unsplash.com/photo-1563245372-f21724e3856d?auto=format&fit=crop&q=80&w=200'
      }
    ]
  }
];

export default function ProductDetailPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = use(params);
  const router = useRouter();
  const { user, triggerToast, refreshCart } = useAuth();

  // Product configurations state
  const [productId, setProductId] = useState('prod_neon_123');
  const [selectedAttributes, setSelectedAttributes] = useState<Record<string, string | number | boolean>>({
    font: 'cursive',
    color: 'Electric Pink',
    backing: 'cut_to_shape',
    size: 'small',
  });
  const [quantity, setQuantity] = useState(1);
  const [customText, setCustomText] = useState('My Custom Glow');
  
  // AI Preview State
  const [aiPreviewImage, setAiPreviewImage] = useState<string | null>(null);
  const [isGeneratingAI, setIsGeneratingAI] = useState(false);

  // Error States
  const [inlineErrors, setInlineErrors] = useState<Record<string, string>>({});
  const [generalError, setGeneralError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Product details variables
  const basePrice = 1200;

  // Calculate dynamic price on-the-fly during render to satisfy ESLint
  let estimatedPrice = basePrice;
  mockNeonSchema.forEach((attr) => {
    const selectedVal = selectedAttributes[attr.key];
    const selectedOption = attr.options?.find((opt) => opt.value === selectedVal);
    if (selectedOption) {
      estimatedPrice += selectedOption.price_delta;
    }
  });
  estimatedPrice *= quantity;

  // Handle attribute selection changes
  const handleAttributeChange = (key: string, value: string | number | boolean) => {
    setSelectedAttributes((prev) => ({
      ...prev,
      [key]: value,
    }));
    // Clear inline error for this key
    if (inlineErrors[key]) {
      setInlineErrors((prev) => {
        const copy = { ...prev };
        delete copy[key];
        return copy;
      });
    }
  };

  // Mock Module 5 AI generation call
  const generateAIPreview = () => {
    setIsGeneratingAI(true);
    setGeneralError(null);
    
    // Simulate generation delay
    setTimeout(() => {
      setIsGeneratingAI(false);
      // Set a mock neon preview image URL
      const mockImages = [
        'https://images.unsplash.com/photo-1563245372-f21724e3856d?auto=format&fit=crop&q=80&w=600',
        'https://images.unsplash.com/photo-1507508064433-641572e9c133?auto=format&fit=crop&q=80&w=600',
        'https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&q=80&w=600'
      ];
      const randomUrl = mockImages[Math.floor(Math.random() * mockImages.length)];
      setAiPreviewImage(randomUrl);
      triggerToast('AI Preview generated successfully!', 'success');
    }, 2500);
  };

  // POST add-to-cart action
  const handleAddToCart = async () => {
    setInlineErrors({});
    setGeneralError(null);

    if (quantity <= 0) {
      triggerToast('Quantity must be at least 1.', 'error');
      return;
    }

    const payload = {
      product_id: productId,
      category_id: slug.includes('neon') ? 'cat_neon' : `cat_${slug.split('-')[0]}`,
      selected_attributes: selectedAttributes,
      quantity,
      custom_text: customText,
      ai_preview_image: aiPreviewImage,
    };

    // Guest Flow Redirect
    if (!user) {
      triggerToast('Please login to add this custom product to your cart.', 'warning');
      sessionStorage.setItem('pending_cart_item', JSON.stringify(payload));
      
      // Delay redirect to let user read toast
      setTimeout(() => {
        router.push('/login');
      }, 800);
      return;
    }

    setIsSubmitting(true);

    try {
      const res = await fetch('/api/cart/items', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      const result = await res.json();

      if (res.status === 201) {
        triggerToast('Item added to cart successfully!', 'success');
        refreshCart();
      } else if (res.status === 400) {
        // Validation Errors
        if (result.errors) {
          setInlineErrors(result.errors);
          triggerToast('Validation failed. Please correct selected attributes.', 'error');
        } else {
          setGeneralError(result.message || 'Invalid product attributes.');
        }
      } else if (res.status === 404) {
        setGeneralError(result.message || 'Product is inactive or no longer exists.');
        triggerToast('Product not available.', 'error');
      } else {
        setGeneralError(result.message || 'Server error adding item.');
      }
    } catch (err) {
      console.error(err);
      setGeneralError('Network error connecting to API.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-bg-void text-text-primary">
      <Header />
      <div className="flex-1 py-12 px-6 max-w-6xl mx-auto w-full">
        <Link href="/cart" className="inline-flex items-center gap-2 text-text-muted hover:text-neon-blue transition-colors duration-200 mb-8 font-semibold">
        <ArrowLeft size={16} /> Back to Shopping Cart
      </Link>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
        {/* Left Column: Visual display & AI Preview */}
        <div className="lg:col-span-6 flex flex-col gap-6">
          <div className="relative aspect-square rounded-xl overflow-hidden glass-panel flex flex-col items-center justify-center p-6 border-white/5 shadow-glow-pink">
            {/* Background design glow */}
            <div className="absolute inset-0 bg-radial-gradient from-neon-pink/10 to-transparent pointer-events-none" />

            {isGeneratingAI ? (
              <div className="flex flex-col items-center gap-4">
                {/* Glowing Scanning Line */}
                <div className="relative w-48 h-48 rounded bg-white/5 border border-white/10 flex items-center justify-center overflow-hidden">
                  <div className="absolute inset-0 bg-gradient-to-b from-neon-pink/20 to-transparent w-full h-1/2 animate-bounce" />
                  <Sparkles className="w-10 h-10 text-neon-pink animate-pulse" />
                </div>
                <span className="text-sm font-semibold text-neon-pink text-glow-pink animate-pulse">
                  AI preview generating...
                </span>
              </div>
            ) : aiPreviewImage ? (
              <div className="relative w-full h-full flex flex-col items-center">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={aiPreviewImage}
                  alt="Custom neon sign preview"
                  className="w-full h-[90%] object-contain rounded-lg border border-white/10"
                />
                <span className="text-xs text-neon-blue text-glow-blue mt-3 font-semibold flex items-center gap-1.5">
                  <Sparkles size={12} /> AI Simulated Preview Active
                </span>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center text-center p-8">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src="https://images.unsplash.com/photo-1563245372-f21724e3856d?auto=format&fit=crop&q=80&w=600"
                  alt="Default Neon Board"
                  className="w-full max-h-64 object-cover rounded-lg border border-white/5 mb-4"
                />
                <p className="text-text-muted text-sm max-w-sm mb-4">
                  Default product catalog view. Use the button below to generate a custom AI rendering of your neon lettering.
                </p>
              </div>
            )}
          </div>

          <button
            type="button"
            onClick={generateAIPreview}
            disabled={isGeneratingAI}
            className="w-full py-3.5 px-6 rounded-lg font-bold bg-gradient-to-r from-neon-pink to-neon-violet text-text-primary flex items-center justify-center gap-2.5 transition-all duration-300 transform hover:scale-[1.02] shadow-glow-pink hover:from-neon-pink hover:to-neon-violet disabled:opacity-50"
          >
            <Sparkles size={18} className="animate-spin-slow" />
            {aiPreviewImage ? 'Re-Generate AI Preview' : 'Generate Custom AI Preview'}
          </button>
        </div>

        {/* Right Column: Configurator Panel */}
        <div className="lg:col-span-6 flex flex-col justify-between">
          <div>
            <div className="mb-6">
              <h1 className="text-4xl font-extrabold font-display text-text-primary text-glow-pink tracking-tight mb-2 capitalize">
                Custom {slug.replace(/-/g, ' ')}
              </h1>
              <p className="text-text-muted text-sm leading-relaxed">
                Handcrafted premium LED neon signs built to your specifications. Type your lettering, configure backing options, size, colors and see the price calculate in real-time.
              </p>
            </div>

            {/* Test Trigger Helper Panel */}
            <div className="p-3.5 mb-6 rounded-lg bg-neon-yellow/5 border border-neon-yellow/20 flex flex-col gap-2">
              <div className="flex items-center gap-2 text-neon-yellow">
                <ShieldAlert size={16} />
                <span className="text-xs font-bold uppercase tracking-wider">Test Control Center</span>
              </div>
              <p className="text-[11px] text-text-muted">
                Test the robust error handling required by the specification:
              </p>
              <div className="flex gap-4">
                <label className="flex items-center gap-2 text-xs cursor-pointer text-text-primary">
                  <input
                    type="checkbox"
                    checked={productId === 'trigger_404_inactive'}
                    onChange={(e) => setProductId(e.target.checked ? 'trigger_404_inactive' : 'prod_neon_123')}
                    className="accent-neon-yellow"
                  />
                  Simulate Inactive Product (Triggers 404)
                </label>
              </div>
            </div>

            {generalError && (
              <div className="p-4 mb-6 rounded-lg bg-neon-pink/10 border border-neon-pink text-text-primary text-sm flex gap-3 items-center">
                <ShieldAlert className="text-neon-pink flex-shrink-0" />
                <span className="font-semibold">{generalError}</span>
              </div>
            )}

            {/* Text input for custom neon lettering */}
            <div className="mb-6">
              <label className="text-sm font-semibold text-text-primary uppercase tracking-wider block mb-2">
                Custom Lettering / Sign Text
              </label>
              <input
                type="text"
                value={customText}
                onChange={(e) => setCustomText(e.target.value)}
                placeholder="Type your name or signage text..."
                className="w-full px-4 py-3 rounded-lg bg-surface-panel border border-white/10 text-text-primary focus:outline-none focus:border-neon-blue focus:ring-1 focus:ring-neon-blue transition-colors duration-200 text-lg font-medium placeholder-white/20"
              />
            </div>

            {/* Configurator Attribute Schema */}
            {mockNeonSchema.map((attr) => (
              <AttributeRenderer
                key={attr.key}
                schema={attr}
                selectedValue={selectedAttributes[attr.key]}
                onChange={(val) => handleAttributeChange(attr.key, val)}
                error={inlineErrors[attr.key]}
              />
            ))}
          </div>

          <div className="border-t border-white/10 pt-6 mt-6">
            <div className="flex justify-between items-center mb-6">
              <div className="flex items-center border border-white/10 rounded-lg bg-surface-panel overflow-hidden">
                <button
                  type="button"
                  onClick={() => setQuantity(Math.max(1, quantity - 1))}
                  className="px-4 py-2 hover:bg-white/5 text-text-primary transition-colors duration-200"
                >
                  <Minus size={14} />
                </button>
                <span className="px-5 py-2 font-bold text-text-primary border-x border-white/10 bg-void-black">
                  {quantity}
                </span>
                <button
                  type="button"
                  onClick={() => setQuantity(quantity + 1)}
                  className="px-4 py-2 hover:bg-white/5 text-text-primary transition-colors duration-200"
                >
                  <Plus size={14} />
                </button>
              </div>

              <div className="text-right">
                <span className="text-xs text-text-muted block font-semibold uppercase tracking-wider">Estimated Price</span>
                <span className="text-3xl font-extrabold text-text-primary text-glow-blue tracking-tight">
                  ₹{estimatedPrice}
                </span>
              </div>
            </div>

            <button
              type="button"
              onClick={handleAddToCart}
              disabled={isSubmitting}
              className="w-full py-4 px-6 rounded-lg font-bold bg-neon-blue text-[#0B0B0F] flex items-center justify-center gap-2.5 transition-all duration-300 transform hover:scale-[1.02] shadow-glow-blue hover:brightness-110 disabled:opacity-50"
            >
              <ShoppingCart size={18} />
              {isSubmitting ? 'Adding Selection...' : 'Add to Shopping Cart'}
            </button>
          </div>
        </div>
      </div>
    </div>
    </div>
  );
}

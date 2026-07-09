import React, { useState, useEffect } from 'react';

/**
 * ProductGallery — Displays product imagery on the detail page.
 *
 * FIX #3: Implements the required type-based display rule:
 *
 *   - pre_designed: Show real product photos from `gallery` / `thumbnail` (original behavior).
 *
 *   - fully_custom: Show `product.category.hero_image` as the primary image until the
 *     user has configured the product. Once configured (`hasBeenConfigured` = true),
 *     display a placeholder slot for the future AI preview image (Module 5 integration).
 *
 * Props:
 *   - product          (required) Full product object from fetchProductBySlug
 *   - hasBeenConfigured (optional) Boolean, defaults to false.
 *                        Set to true once the user completes a configurator step.
 *   - aiPreviewUrl      (optional) String URL for the AI-generated preview image.
 *                        Module 5 will supply this once the AI preview feature ships.
 */
export default function ProductGallery({ product, hasBeenConfigured = false, aiPreviewUrl = null }) {
  const { gallery, thumbnail, category, title, type } = product;
  const [activeIndex, setActiveIndex] = useState(0);

  // Reset the active index on product change
  useEffect(() => {
    setActiveIndex(0);
  }, [product]);

  const categoryAccentColor = category?.accent_color || 'var(--accent-cyan)';

  // ── FIX #3: Type-aware image selection ────────────────────────────────
  const isFullyCustom = type === 'fully_custom';

  if (isFullyCustom) {
    // ── FULLY CUSTOM display rule ──────────────────────────────────────
    // Before configuration: show category hero image as primary visual.
    // After configuration:  show AI preview placeholder (or actual URL when Module 5 provides it).
    const heroImage = category?.hero_image
      || 'https://images.unsplash.com/photo-1513519245088-0e12902e5a38?auto=format&fit=crop&q=80&w=800';

    if (!hasBeenConfigured) {
      // Pre-configuration state: category hero image
      return (
        <div className="product-gallery-container fade-in">
          <div
            className="main-preview-frame glass-panel"
            style={{ '--cat-accent': categoryAccentColor }}
          >
            <img
              src={heroImage}
              alt={`${category?.name || 'Category'} — configure to see your design`}
              className="main-preview-image"
            />
            {/* Informational tip for unconfigured fully-custom products */}
            <span className="gallery-tip">
              Configure this product to preview your custom design
            </span>
          </div>
        </div>
      );
    }

    // Post-configuration state: AI preview slot
    // `aiPreviewUrl` will be populated by Module 5 once the AI preview feature ships.
    return (
      <div className="product-gallery-container fade-in">
        <div
          className="main-preview-frame glass-panel"
          style={{ '--cat-accent': categoryAccentColor }}
        >
          {aiPreviewUrl ? (
            // Module 5 has provided an AI-generated preview image
            <>
              <img
                src={aiPreviewUrl}
                alt={`${title} — AI-generated preview`}
                className="main-preview-image"
              />
              <span className="ai-preview-badge">
                <span className="sparkle-icon">✨</span> AI Preview
              </span>
            </>
          ) : (
            // Placeholder until Module 5 supplies the AI preview URL
            <div className="flex-center" style={{ width: '100%', height: '100%', flexDirection: 'column', gap: '1rem' }}>
              <div className="ai-spinner-container">
                <div
                  className="ai-spinner"
                  style={{ borderTopColor: categoryAccentColor }}
                />
                <span className="ai-spinner-text">
                  AI preview will appear here once generated
                </span>
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }

  // ── PRE-DESIGNED display rule (default) ──────────────────────────────
  // Show real product photos from gallery / thumbnail as a slideshow.
  let slideshowImages = gallery && gallery.length > 0 ? gallery : [thumbnail];
  slideshowImages = slideshowImages.filter(Boolean);
  const mainImage = slideshowImages[activeIndex] || 'https://images.unsplash.com/photo-1513519245088-0e12902e5a38?auto=format&fit=crop&q=80&w=800';
  const showSlideshow = slideshowImages.length > 1;

  return (
    <div className="product-gallery-container fade-in">
      <div 
        className="main-preview-frame glass-panel"
        style={{ '--cat-accent': categoryAccentColor }}
      >
        <img 
          src={mainImage} 
          alt={title} 
          className="main-preview-image" 
          key={mainImage} // triggers animation on change
        />
      </div>

      {showSlideshow && (
        <div className="gallery-thumbnails">
          {slideshowImages.map((img, idx) => (
            <button
              key={idx}
              className={`gallery-thumb-btn ${idx === activeIndex ? 'active' : ''}`}
              onClick={() => setActiveIndex(idx)}
              style={{
                borderColor: idx === activeIndex ? categoryAccentColor : 'var(--border-glass)'
              }}
              aria-label={`View slide ${idx + 1}`}
            >
              <img src={img} alt={`${title} detail ${idx + 1}`} className="thumb-image" />
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

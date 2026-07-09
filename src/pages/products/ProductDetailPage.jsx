import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { productApi } from '../../services/api/productApi';
import ProductGallery from '../../components/products/ProductGallery';

/**
 * FIX #1: Configurator attribute renderer
 * 
 * Renders a single attribute from the category's attribute_schema using the
 * REAL backend shape:
 *   { key, label, type, options: [{value, label, price_delta}], required }
 * 
 * Supported types: select, color_swatch, image_swatch, toggle, slider, number, text
 * Removed old 'color' and 'image_upload' type cases that don't match real API types.
 */
function AttributeInput({ attr, value, onChange, accentColor }) {
  // FIX #1: Use attr.key as the identifier, attr.label for display
  const attrKey = attr.key;
  const attrLabel = attr.label || attr.key;

  switch (attr.type) {
    // ── SELECT: dropdown with options ──────────────────────────────────
    case 'select':
      return (
        <div className="configurator-field" key={attrKey}>
          <label className="configurator-label">
            {attrLabel}
            {attr.required && <span className="required-mark">*</span>}
          </label>
          <select
            className="form-select configurator-select"
            value={value || ''}
            onChange={(e) => onChange(attrKey, e.target.value)}
          >
            <option value="">Select {attrLabel}</option>
            {/* FIX #1: options are objects with {value, label, price_delta} */}
            {(attr.options || []).map(opt => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
                {opt.price_delta ? ` (${opt.price_delta > 0 ? '+' : ''}₹${opt.price_delta})` : ''}
              </option>
            ))}
          </select>
        </div>
      );

    // ── COLOR_SWATCH: visual color circles ────────────────────────────
    // FIX #1: New type — replaces old 'color' case
    case 'color_swatch':
      return (
        <div className="configurator-field" key={attrKey}>
          <label className="configurator-label">
            {attrLabel}
            {attr.required && <span className="required-mark">*</span>}
          </label>
          <div className="swatch-options">
            {(attr.options || []).map(opt => (
              <button
                key={opt.value}
                type="button"
                className={`color-swatch-btn ${value === opt.value ? 'active' : ''}`}
                style={{
                  backgroundColor: opt.value,
                  borderColor: value === opt.value ? accentColor : 'var(--border-glass)',
                  boxShadow: value === opt.value ? `0 0 8px ${opt.value}80` : 'none'
                }}
                onClick={() => onChange(attrKey, opt.value)}
                title={`${opt.label}${opt.price_delta ? ` (${opt.price_delta > 0 ? '+' : ''}₹${opt.price_delta})` : ''}`}
                aria-label={opt.label}
              />
            ))}
          </div>
          {/* Show selected swatch label */}
          {value && (
            <span className="swatch-selected-label">
              {(attr.options || []).find(o => o.value === value)?.label || value}
            </span>
          )}
        </div>
      );

    // ── IMAGE_SWATCH: visual image option tiles ───────────────────────
    // FIX #1: New type — replaces old 'image_upload' case
    case 'image_swatch':
      return (
        <div className="configurator-field" key={attrKey}>
          <label className="configurator-label">
            {attrLabel}
            {attr.required && <span className="required-mark">*</span>}
          </label>
          <div className="swatch-options image-swatch-grid">
            {(attr.options || []).map(opt => (
              <button
                key={opt.value}
                type="button"
                className={`image-swatch-btn ${value === opt.value ? 'active' : ''}`}
                style={{
                  borderColor: value === opt.value ? accentColor : 'var(--border-glass)'
                }}
                onClick={() => onChange(attrKey, opt.value)}
                title={`${opt.label}${opt.price_delta ? ` (${opt.price_delta > 0 ? '+' : ''}₹${opt.price_delta})` : ''}`}
              >
                <img src={opt.value} alt={opt.label} className="image-swatch-img" />
                <span className="image-swatch-label">{opt.label}</span>
              </button>
            ))}
          </div>
        </div>
      );

    // ── TOGGLE: boolean on/off switch ─────────────────────────────────
    // FIX #1: New type — not present in old code
    case 'toggle':
      return (
        <div className="configurator-field" key={attrKey}>
          <label className="toggle-container configurator-toggle">
            <input
              type="checkbox"
              className="toggle-checkbox"
              checked={value === true || value === 'true'}
              onChange={(e) => onChange(attrKey, e.target.checked)}
            />
            <span className="toggle-slider"></span>
            <span className="toggle-label">
              {attrLabel}
              {attr.required && <span className="required-mark">*</span>}
            </span>
          </label>
          {/* Show price impact if any option defines it */}
          {(attr.options || []).length > 0 && attr.options[0].price_delta && (
            <span className="configurator-price-hint">
              {attr.options[0].price_delta > 0 ? '+' : ''}₹{attr.options[0].price_delta}
            </span>
          )}
        </div>
      );

    // ── SLIDER: range input ───────────────────────────────────────────
    // FIX #1: New type — not present in old code
    case 'slider': {
      // Slider options define min/max/step via the options array
      const min = attr.options?.[0]?.value ?? 0;
      const max = attr.options?.[attr.options.length - 1]?.value ?? 100;
      const currentVal = value ?? min;
      // Find the matching option for price delta display
      const matchedOpt = (attr.options || []).find(o => String(o.value) === String(currentVal));
      return (
        <div className="configurator-field" key={attrKey}>
          <label className="configurator-label">
            {attrLabel}: <strong>{currentVal}</strong>
            {attr.required && <span className="required-mark">*</span>}
            {matchedOpt?.price_delta ? (
              <span className="configurator-price-hint" style={{ marginLeft: '0.5rem' }}>
                ({matchedOpt.price_delta > 0 ? '+' : ''}₹{matchedOpt.price_delta})
              </span>
            ) : null}
          </label>
          <input
            type="range"
            className="configurator-slider"
            min={min}
            max={max}
            value={currentVal}
            onChange={(e) => onChange(attrKey, parseFloat(e.target.value))}
            style={{ accentColor }}
          />
          <div className="slider-range-labels">
            <span>{min}</span>
            <span>{max}</span>
          </div>
        </div>
      );
    }

    // ── NUMBER: numeric input field ───────────────────────────────────
    // FIX #1: New type — not present in old code
    case 'number':
      return (
        <div className="configurator-field" key={attrKey}>
          <label className="configurator-label">
            {attrLabel}
            {attr.required && <span className="required-mark">*</span>}
          </label>
          <input
            type="number"
            className="form-input configurator-number"
            value={value ?? ''}
            onChange={(e) => onChange(attrKey, e.target.value === '' ? '' : parseFloat(e.target.value))}
            placeholder={`Enter ${attrLabel}`}
            min={attr.options?.[0]?.value}
            max={attr.options?.[attr.options.length - 1]?.value}
          />
          {/* Show price delta for current value if options define it */}
          {(attr.options || []).find(o => String(o.value) === String(value))?.price_delta && (
            <span className="configurator-price-hint">
              {(attr.options || []).find(o => String(o.value) === String(value)).price_delta > 0 ? '+' : ''}
              ₹{(attr.options || []).find(o => String(o.value) === String(value)).price_delta}
            </span>
          )}
        </div>
      );

    // ── TEXT: free-form text input (kept from original) ───────────────
    case 'text':
      return (
        <div className="configurator-field" key={attrKey}>
          <label className="configurator-label">
            {attrLabel}
            {attr.required && <span className="required-mark">*</span>}
          </label>
          <input
            type="text"
            className="form-input configurator-text"
            value={value || ''}
            onChange={(e) => onChange(attrKey, e.target.value)}
            placeholder={`Enter ${attrLabel}`}
          />
        </div>
      );

    // ── Unknown type fallback ─────────────────────────────────────────
    default:
      return (
        <div className="configurator-field" key={attrKey}>
          <label className="configurator-label">
            {attrLabel}
            {attr.required && <span className="required-mark">*</span>}
          </label>
          <input
            type="text"
            className="form-input configurator-text"
            value={value || ''}
            onChange={(e) => onChange(attrKey, e.target.value)}
            placeholder={`Enter ${attrLabel}`}
          />
          <span className="configurator-hint">Unsupported type: {attr.type}</span>
        </div>
      );
  }
}

export default function ProductDetailPage() {
  const { slug } = useParams();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  // FIX #10: retryTrigger ensures the Retry button always re-triggers the fetch
  // by incrementing a counter used as a useEffect dependency
  const [retryTrigger, setRetryTrigger] = useState(0);

  // FIX #1: Configurator state — keyed by attr.key from attribute_schema
  const [configValues, setConfigValues] = useState({});

  useEffect(() => {
    async function loadProduct() {
      setLoading(true);
      setError(null);
      try {
        const response = await productApi.fetchProductBySlug(slug);
        if (!response || !response.data || response.data.is_active === false) {
          setError('404');
        } else {
          setProduct(response.data);
          // FIX #1: Initialize configurator values from default_attributes if they match schema keys
          const schema = response.data.category?.attribute_schema || [];
          const defaults = response.data.default_attributes || {};
          const initial = {};
          schema.forEach(attr => {
            // FIX #1: Use attr.key as identifier
            if (defaults[attr.key] !== undefined) {
              initial[attr.key] = defaults[attr.key];
            }
          });
          setConfigValues(initial);
        }
      } catch (err) {
        // FIX #6: Store the actual error — it will be differentiated from 404 below
        setError(err.message || 'Error occurred loading product.');
      } finally {
        setLoading(false);
      }
    }

    loadProduct();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [slug, retryTrigger]);

  // FIX #1: Handler for configurator attribute changes
  const handleConfigChange = (key, value) => {
    setConfigValues(prev => ({ ...prev, [key]: value }));
  };

  if (loading) {
    return (
      <div className="detail-loading-container main-content fade-in">
        <div className="skeleton-detail-layout">
          <div className="skeleton skeleton-detail-gallery"></div>
          <div className="skeleton-detail-info">
            <div className="skeleton skeleton-title"></div>
            <div className="skeleton skeleton-price" style={{ width: '25%', marginTop: '1.5rem' }}></div>
            <div className="skeleton skeleton-text" style={{ height: '80px', marginTop: '2rem' }}></div>
            <div className="skeleton skeleton-title" style={{ height: '40px', marginTop: '2rem' }}></div>
          </div>
        </div>
      </div>
    );
  }

  // FIX #6: Non-404 errors get their own distinct message and retry action,
  // separate from the "Product Unavailable / discontinued" 404 display.
  if (error && error !== '404') {
    return (
      <div className="unavailable-page-container main-content fade-in">
        <div className="error-panel glass-panel text-center">
          <div className="unavailable-symbol" style={{ color: '#ff3b30' }}>⚠️</div>
          <h2>Error Loading Product</h2>
          {/* FIX #6: Show the actual error message so network/server failures are distinguishable */}
          <p>Something went wrong while loading this product.</p>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
            {error}
          </p>
          <div className="unavailable-actions">
            {/* FIX #6 + #10: Retry button increments retryTrigger to force re-fetch */}
            <button className="action-btn buy-btn" onClick={() => setRetryTrigger(prev => prev + 1)}>
              Retry Loading
            </button>
            <Link to="/" className="action-btn configure-btn" style={{ marginLeft: '1rem' }}>
              Return to Catalog
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // 404 / Inactive display rule
  if (error === '404' || !product) {
    return (
      <div className="unavailable-page-container main-content fade-in">
        <div className="error-panel glass-panel text-center">
          <div className="unavailable-symbol">⚡</div>
          <h2>Product Unavailable</h2>
          <p>The product you are looking for does not exist, has been discontinued, or is currently deactivated.</p>
          <div className="unavailable-actions">
            <Link to="/" className="action-btn buy-btn">
              Return to Catalog
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const categoryAccentColor = product.category?.accent_color || 'var(--accent-cyan)';
  const isOutOfStock = product.stock_status === 'out_of_stock';

  // FIX #1: Get the attribute_schema from the category (real backend shape)
  const attributeSchema = product.category?.attribute_schema || [];

  return (
    <div 
      className="product-detail-page fade-in"
      style={{ '--cat-accent': categoryAccentColor }}
    >
      <div className="detail-header-nav">
        <Link to="/" className="back-link">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" width="16" height="16">
            <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" />
          </svg>
          <span>Back to Catalog</span>
        </Link>
        <span className="nav-divider">/</span>
        <span className="nav-current">{product.title}</span>
      </div>

      <div className="detail-layout">
        {/* Gallery Panel */}
        <div className="detail-gallery-panel">
          <ProductGallery product={product} />
        </div>

        {/* Info & Configurator Panel */}
        <div className="detail-info-panel glass-panel">
          <div className="detail-meta">
            <span className="badge badge-featured" style={{ background: `rgba(255, 255, 255, 0.05)`, color: categoryAccentColor, borderColor: `rgba(255, 255, 255, 0.1)` }}>
              {product.category?.name}
            </span>
            <div className="views-counter" title="Total Product Views">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" width="16" height="16">
                <path strokeLinecap="round" strokeLinejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" />
                <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <span>{product.views} views</span>
            </div>
          </div>

          <h1 className="detail-title">{product.title}</h1>

          <div className="detail-rating-row">
            <div className="stars-wrapper">
              {Math.floor(product.rating_avg)} ★
            </div>
            <span className="rating-text">({product.rating_avg.toFixed(1)} avg rating)</span>
            <span className="status-indicator">
              {isOutOfStock ? (
                <span className="badge badge-stock-out">Out of Stock</span>
              ) : (
                <span className="badge badge-stock-in">In Stock</span>
              )}
            </span>
          </div>

          <div className="detail-price-row">
            <span className="detail-base-label">Base Price</span>
            <span className="detail-price" style={{ color: categoryAccentColor }}>
              ₹{product.base_price.toFixed(2)}
            </span>
          </div>

          <p className="detail-description">{product.description}</p>

          {/* FIX #1: Configurator section — renders attribute_schema with real backend types */}
          {attributeSchema.length > 0 && (
            <div className="detail-configurator-box">
              <h3 className="configurator-title" style={{ borderLeftColor: categoryAccentColor }}>
                Customize Your Product
              </h3>
              <div className="configurator-fields">
                {attributeSchema.map(attr => (
                  <AttributeInput
                    key={attr.key}
                    attr={attr}
                    value={configValues[attr.key]}
                    onChange={handleConfigChange}
                    accentColor={categoryAccentColor}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Default Specifications attributes (shown when no schema / as fallback) */}
          {product.default_attributes && Object.keys(product.default_attributes).length > 0 && attributeSchema.length === 0 && (
            <div className="detail-configurator-box">
              <h3 className="configurator-title" style={{ borderLeftColor: categoryAccentColor }}>
                Default Specifications
              </h3>
              <div className="default-attributes-grid" style={{ marginTop: '1rem', display: 'flex', flexWrap: 'wrap', gap: '0.75rem' }}>
                {Object.entries(product.default_attributes).map(([key, val]) => (
                  <div key={key} style={{
                    background: 'rgba(255, 255, 255, 0.03)',
                    border: '1px solid var(--border-glass)',
                    padding: '0.5rem 1rem',
                    borderRadius: '8px',
                    fontSize: '0.85rem'
                  }}>
                    <strong style={{ color: categoryAccentColor }}>{key}:</strong> <span style={{ color: 'var(--text-primary)' }}>{val}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="detail-actions" style={{ marginTop: '2rem' }}>
            <Link
              to={`/products/${product.slug}/configure`}
              className={`add-to-cart-btn ${isOutOfStock ? 'disabled' : ''}`}
              style={{ 
                backgroundColor: isOutOfStock ? 'var(--text-muted)' : categoryAccentColor,
                boxShadow: isOutOfStock ? 'none' : `0 0 20px ${categoryAccentColor}4D`,
                textAlign: 'center',
                textDecoration: 'none',
                display: 'block',
                width: '100%',
                padding: '1rem',
                borderRadius: '8px',
                fontWeight: '600',
                color: '#000',
                cursor: isOutOfStock ? 'not-allowed' : 'pointer'
              }}
              onClick={(e) => {
                if (isOutOfStock) e.preventDefault();
              }}
            >
              Configure This Design
            </Link>
          </div>
        </div>
      </div>

      {/* FIX #3: Specifications Block — now handles specifications as a plain object/dictionary
          instead of assuming it's an array. Uses Object.entries() to iterate key-value pairs. */}
      {product.specifications && Object.entries(product.specifications || {}).length > 0 && (
        <div className="detail-specs-section glass-panel">
          <h2>Product Specifications</h2>
          <table className="specs-table">
            <tbody>
              {/* FIX #3: Iterate with Object.entries() for object/dictionary shape */}
              {Object.entries(product.specifications).map(([key, value]) => (
                <tr key={key}>
                  <td className="spec-name">{key}</td>
                  <td className="spec-val">{value}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

import React, { useState, useEffect, useRef } from 'react';
import './AIPreviewPanel.css';

/**
 * AIPreviewPanel Component (m5_Frontend1)
 * 
 * Lives on the Product detail page alongside the product image gallery.
 * Handles toggling into preview mode, loading state scan-lines, success previews,
 * rate limit states, and stale configuration warnings.
 * 
 * @param {Object} props
 * @param {Object} props.category - The category schema from Module 2 (includes attributes schema)
 * @param {Object} props.selectedAttributes - The current user-configured product attributes
 * @param {Object} props.user - The authenticated user object (null for guests)
 * @param {string} props.defaultProductImage - The default static image for the product
 */
export default function AIPreviewPanel({
  category,
  selectedAttributes,
  user,
  defaultProductImage
}) {
  // Component States
  const [activeTab, setActiveTab] = useState('photos'); // 'photos' | 'preview'
  const [previewState, setPreviewState] = useState('initial'); // 'initial' | 'loading' | 'success' | 'error'
  const [outputImageUrl, setOutputImageUrl] = useState(null);
  const [generationId, setGenerationId] = useState(null);
  const [fromCache, setFromCache] = useState(false);
  const [isStale, setIsStale] = useState(false);
  const [limitScope, setLimitScope] = useState(null); // 'session' | 'user'
  const [errorStatus, setErrorStatus] = useState(null); // 400 | 429 | 502 | 504 | etc.

  // Refs for tracking changes
  const isFirstChange = useRef(true);
  const lastGeneratedAttributes = useRef(null);

  // Security Helper: Strip prompt injection keywords and excessive characters
  const sanitizeCustomText = (text) => {
    if (!text) return '';
    const injectionPatterns = [
      /ignore\s+(previous\s+)?instructions/gi,
      /system\s+prompt/gi,
      /translate\s+to/gi,
      /do\s+not\s+spell/gi,
      /you\s+are\s+now/gi,
      /override/gi
    ];
    let clean = text;
    injectionPatterns.forEach(pattern => {
      clean = clean.replace(pattern, '');
    });
    clean = clean.replace(/[^a-zA-Z0-9\s.,!?'"-]/g, '');
    return clean.trim();
  };

  // Determine if a changed attribute affects the AI preview according to schema
  const getAffectsPreviewKeys = () => {
    if (!category || !category.attributes) return [];
    return category.attributes
      .filter(attr => attr.affects_ai_preview)
      .map(attr => attr.key);
  };

  // Watch attributes configuration changes
  useEffect(() => {
    if (!category) return;
    
    const previewKeys = getAffectsPreviewKeys();
    
    // Skip checking on initial render
    if (isFirstChange.current) {
      isFirstChange.current = false;
      return;
    }

    // Auto-switch to preview tab on first change of preview-affecting attributes
    if (activeTab === 'photos') {
      setActiveTab('preview');
      generatePreview();
      return;
    }

    // Check if the current selection is stale relative to the generated preview
    if (lastGeneratedAttributes.current) {
      const changedKeys = previewKeys.filter(key => 
        selectedAttributes[key] !== lastGeneratedAttributes.current[key]
      );
      
      if (changedKeys.length > 0) {
        setIsStale(true);
      } else {
        setIsStale(false);
      }
    }
  }, [selectedAttributes, category]);

  // Main generator orchestration
  const generatePreview = async () => {
    setPreviewState('loading');
    setIsStale(false);
    setErrorStatus(null);
    setLimitScope(null);

    // Apply client-side prompt sanitization
    const sanitizedAttributes = { ...selectedAttributes };
    if (sanitizedAttributes.custom_text) {
      sanitizedAttributes.custom_text = sanitizeCustomText(sanitizedAttributes.custom_text);
    }

    const requestBody = {
      category_id: category?.id || '',
      product_id: null, // Custom configured item
      selected_attributes: sanitizedAttributes,
      session_id: user ? null : (localStorage.getItem('galaxy_guest_session_id') || '')
    };

    try {
      const response = await fetch('/api/ai/generate-preview', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody)
      });

      const resJson = await response.json();

      if (response.ok && resJson.success) {
        const { output_image_url, from_cache, generation_id } = resJson.data;
        
        setOutputImageUrl(output_image_url);
        setGenerationId(generation_id);
        setFromCache(from_cache);
        
        // Cache current attributes configuration
        lastGeneratedAttributes.current = { ...selectedAttributes };
        setPreviewState('success');
      } else {
        // Handle validation error (400), rate limit (429) or gateway errors (502/504)
        setErrorStatus(response.status);
        if (response.status === 429) {
          setLimitScope(resJson.data?.limit_scope || 'session');
        }
        setPreviewState('error');
      }
    } catch (err) {
      setErrorStatus(500);
      setPreviewState('error');
    }
  };

  return (
    <div className="ai-preview-panel-container">
      {/* Tab Navigation */}
      <div className="tab-navigation" role="tablist">
        <button 
          className={`tab-btn ${activeTab === 'photos' ? 'active' : ''}`}
          onClick={() => setActiveTab('photos')}
          role="tab"
          aria-selected={activeTab === 'photos'}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 12m-9 0a9 9 0 1 0 18 0a9 9 0 1 0 -18 0"/><path d="M12 10m-3 0a3 3 0 1 0 6 0a3 3 0 1 0 -6 0"/><path d="M6.162 17.006a8 8 0 0 1 11.676 0"/></svg>
          Product Photos
        </button>
        <button 
          className={`tab-btn ${activeTab === 'preview' ? 'active' : ''}`}
          onClick={() => setActiveTab('preview')}
          role="tab"
          aria-selected={activeTab === 'preview'}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 3a9 9 0 0 0 -9 9a9 9 0 0 0 9 9a9 9 0 0 0 9 -9a9 9 0 0 0 -9 -9z"/><path d="M12 8l0 4"/><path d="M12 16l.01 0"/><path d="M9 12l6 0"/></svg>
          AI Preview <span className="badge-sparkle">AI</span>
        </button>
      </div>

      {/* Tab Content */}
      <div className="tab-content">
        {activeTab === 'photos' ? (
          /* Product Photos View */
          <div className="gallery-wrapper">
            <img src={defaultProductImage} alt="Product View" className="product-main-image" />
            <div className="gallery-thumbnails">
              <div className="thumb active">
                <img src={defaultProductImage} alt="Thumbnail view" />
              </div>
            </div>
          </div>
        ) : (
          /* AI Preview Card View */
          <div className="ai-preview-card">
            
            {/* 1. INITIAL PLACEHOLDER STATE */}
            {previewState === 'initial' && (
              <div className="ai-state-container initial-box">
                <div className="glow-sparkle-icon">
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M12 3l1.912 5.885h6.19l-5.008 3.638l1.912 5.885l-5.007 -3.637l-5.007 3.637l1.911 -5.885l-5.007 -3.638h6.19z"/></svg>
                </div>
                <h3>Create Your AI Preview</h3>
                <p>Customize the color, font, or text to dynamically render an AI lighting preview of your custom sign.</p>
              </div>
            )}

            {/* 2. LOADING STATE (With glow scanline) */}
            {previewState === 'loading' && (
              <div className="ai-state-container loading-box">
                <div className="loading-gradient-pulse">
                  <div className="scanline"></div>
                </div>
                <div className="loading-info-overlay">
                  <p className="loading-text">Generating AI Preview...</p>
                  <p className="loading-subtext">Assembling templates and rendering lighting vectors</p>
                </div>
              </div>
            )}

            {/* 3. SUCCESS STATE */}
            {previewState === 'success' && (
              <div className="ai-state-container success-box">
                <div className={`preview-image-wrapper ${isStale ? 'stale' : ''}`}>
                  <img src={outputImageUrl} alt="AI Generated Custom Neon Sign" />
                  
                  {/* Stale Banner overlay */}
                  {isStale && (
                    <div className="stale-banner">
                      <div className="stale-banner-content">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 9v4"/><path d="M12 17h.01"/><path d="M5 19h14a2 2 0 0 0 1.84 -2.75L13.84 4a2 2 0 0 0 -3.68 0L3.16 16.25A2 2 0 0 0 5 19z"/></svg>
                        <span>Preview may be outdated</span>
                        <button className="btn-regen-stale" onClick={generatePreview}>Regenerate</button>
                      </div>
                    </div>
                  )}
                </div>
                
                <div className="preview-footer">
                  <p className="ai-disclaimer">AI-generated approximation — final product may vary.</p>
                  <div className="preview-meta">
                    {fromCache && <span className="cache-badge">Served from cache</span>}
                    {generationId && <span className="gen-id-badge">Gen ID: {generationId}</span>}
                    <button className="btn-regenerate-main" onClick={generatePreview}>
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M20 11a8.1 8.1 0 0 0 -15.5 -2m-.5 -4v4h4"/><path d="M4 13a8.1 8.1 0 0 0 15.5 2m.5 4v-4h-4"/></svg>
                      Regenerate
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* 4. ERROR & RATE-LIMIT & INVALID STATES */}
            {previewState === 'error' && (
              <div className="ai-state-container error-box">
                <div className="error-visual">
                  <div className="error-icon-wrapper">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M3 12a9 9 0 1 0 18 0a9 9 0 0 0 -18 0"/><path d="M12 8v4"/><path d="M12 16h.01"/></svg>
                  </div>
                </div>
                <div className="error-details">
                  {errorStatus === 429 ? (
                    <>
                      <h3>Daily Limit Reached</h3>
                      <p>
                        {limitScope === 'user'
                          ? 'Daily limit reached, try again tomorrow.'
                          : "You've used your free previews for now — sign up to keep designing."}
                      </p>
                    </>
                  ) : errorStatus === 400 ? (
                    <>
                      <h3>Invalid Configuration</h3>
                      <p>One or more of the selected attributes are invalid. Please check your configurations according to the validation rules.</p>
                    </>
                  ) : (
                    <>
                      <h3>Preview Unavailable</h3>
                      <p>
                        {errorStatus === 504 
                          ? 'The AI preview generator is taking longer than usual. Please try again.'
                          : 'An error occurred while generating the preview. Our team has been notified.'}
                      </p>
                    </>
                  )}
                  <button className="btn-primary" onClick={generatePreview}>Try Again</button>
                </div>
              </div>
            )}

          </div>
        )}
      </div>
    </div>
  );
}

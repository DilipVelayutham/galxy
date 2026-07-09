import React, { useState, useEffect } from 'react';
import { productApi } from '../../services/api/productApi';

/**
 * ProductFilterBar — Sidebar filter controls for the product listing page.
 *
 * FIX #8: Tag filter pills are now derived from actual product data via
 * productApi.fetchProductTags(), instead of a hard-coded commonTags list.
 * This ensures the tag vocabulary stays in sync with the real product catalog.
 *
 * Also accepts an optional `products` prop from the parent page so tags can
 * be supplemented from the currently loaded result set.
 */
export default function ProductFilterBar({ filters, onFilterChange, onClearFilters, products = [] }) {
  const [categories, setCategories] = useState([]);
  const [loadingCats, setLoadingCats] = useState(false);

  // FIX #8: Tags derived from actual loaded product data, not hard-coded.
  // Falls back to fetching from the API if no products are passed.
  const [availableTags, setAvailableTags] = useState([]);

  useEffect(() => {
    async function loadCategories() {
      setLoadingCats(true);
      try {
        const cats = await productApi.fetchCategories();
        setCategories(cats);
      } catch (err) {
        console.error('Failed to load categories', err);
      } finally {
        setLoadingCats(false);
      }
    }
    loadCategories();
  }, []);

  // FIX #8: Load tags from actual product data or from the API
  useEffect(() => {
    async function loadTags() {
      try {
        const tags = await productApi.fetchProductTags();
        setAvailableTags(tags);
      } catch (err) {
        console.error('Failed to load product tags', err);
        // FIX #8: If tag fetch fails, derive from the currently loaded products
        // as a last resort
        if (products.length > 0) {
          const tagSet = new Set();
          products.forEach(p => {
            if (p.tags && Array.isArray(p.tags)) {
              p.tags.forEach(t => tagSet.add(t));
            }
          });
          setAvailableTags(Array.from(tagSet).sort());
        }
      }
    }
    loadTags();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // FIX #8: Supplement available tags with tags from currently loaded products
  // (in case the API fetch didn't cover all products in the current view)
  useEffect(() => {
    if (products.length > 0) {
      setAvailableTags(prev => {
        const tagSet = new Set(prev);
        products.forEach(p => {
          if (p.tags && Array.isArray(p.tags)) {
            p.tags.forEach(t => tagSet.add(t));
          }
        });
        const merged = Array.from(tagSet).sort();
        // Only update if there are new tags
        if (merged.length !== prev.length) {
          return merged;
        }
        return prev;
      });
    }
  }, [products]);

  const handleCategoryClick = (categorySlug) => {
    // Toggle category or set it
    const newCategory = filters.category === categorySlug ? '' : categorySlug;
    onFilterChange('category', newCategory);
  };

  const handlePriceChange = (e, field) => {
    const value = e.target.value;
    onFilterChange(field, value);
  };

  const handleTagToggle = (tag) => {
    let currentTags = filters.tags ? filters.tags.split(',').filter(Boolean) : [];
    if (currentTags.includes(tag)) {
      currentTags = currentTags.filter(t => t !== tag);
    } else {
      currentTags.push(tag);
    }
    onFilterChange('tags', currentTags.join(','));
  };

  const handleFeaturedToggle = () => {
    onFilterChange('featured', !filters.featured);
  };

  const handleSortChange = (e) => {
    onFilterChange('sort', e.target.value);
  };

  const activeTags = filters.tags ? filters.tags.split(',') : [];

  return (
    <aside className="filter-bar glass-panel fade-in">
      <div className="filter-header">
        <h2>Filters</h2>
        <button className="clear-filters-btn" onClick={onClearFilters}>
          Clear All
        </button>
      </div>

      {/* Sort Section */}
      <div className="filter-section">
        <label className="form-label" htmlFor="filter-sort">Sort By</label>
        <select 
          id="filter-sort"
          className="form-select w-full"
          value={filters.sort || 'newest'}
          onChange={handleSortChange}
        >
          <option value="newest">Newest Additions</option>
          <option value="price_asc">Price: Low to High</option>
          <option value="price_desc">Price: High to Low</option>
          <option value="popular">Popularity / Views</option>
        </select>
      </div>

      {/* Category List */}
      <div className="filter-section">
        <h3>Categories</h3>
        {loadingCats ? (
          <div className="cats-skeleton">
            <div className="skeleton cat-skeleton-item"></div>
            <div className="skeleton cat-skeleton-item"></div>
            <div className="skeleton cat-skeleton-item"></div>
          </div>
        ) : (
          <div className="category-options">
            <button 
              className={`category-option-btn ${!filters.category ? 'active' : ''}`}
              onClick={() => onFilterChange('category', '')}
            >
              All Categories
            </button>
            {categories.map(cat => (
              <button
                key={cat.slug}
                style={{
                  '--cat-accent': cat.accent_color,
                  borderColor: filters.category === cat.slug ? cat.accent_color : 'transparent'
                }}
                className={`category-option-btn ${filters.category === cat.slug ? 'active' : ''}`}
                onClick={() => handleCategoryClick(cat.slug)}
              >
                <span className="cat-bullet" style={{ backgroundColor: cat.accent_color }}></span>
                {cat.name}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Price Inputs */}
      <div className="filter-section">
        <h3>Price Range (₹)</h3>
        <div className="price-inputs-grid">
          <div className="price-field">
            <span className="price-symbol">₹</span>
            <input 
              type="number" 
              placeholder="Min" 
              value={filters.min_price || ''} 
              onChange={(e) => handlePriceChange(e, 'min_price')}
              className="price-input"
              min="0"
            />
          </div>
          <span className="price-range-connector">to</span>
          <div className="price-field">
            <span className="price-symbol">₹</span>
            <input 
              type="number" 
              placeholder="Max" 
              value={filters.max_price || ''} 
              onChange={(e) => handlePriceChange(e, 'max_price')}
              className="price-input"
              min="0"
            />
          </div>
        </div>
      </div>

      {/* FIX #8: Tag Pills — derived from actual product data, not hard-coded */}
      <div className="filter-section">
        <h3>Filter by Tag</h3>
        <div className="tags-pills-container">
          {availableTags.length > 0 ? (
            availableTags.map(tag => {
              const isSelected = activeTags.includes(tag);
              return (
                <button
                  key={tag}
                  className={`tag-pill-btn ${isSelected ? 'active' : ''}`}
                  onClick={() => handleTagToggle(tag)}
                >
                  {isSelected && <span className="pill-dot">•</span>}
                  {tag}
                </button>
              );
            })
          ) : (
            <span className="tags-loading-hint" style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
              Loading tags…
            </span>
          )}
        </div>
      </div>

      {/* Featured Toggle */}
      <div className="filter-section border-top">
        <label className="toggle-container">
          <input 
            type="checkbox" 
            checked={!!filters.featured} 
            onChange={handleFeaturedToggle}
            className="toggle-checkbox"
          />
          <span className="toggle-slider"></span>
          <span className="toggle-label">Featured Products Only</span>
        </label>
      </div>
    </aside>
  );
}

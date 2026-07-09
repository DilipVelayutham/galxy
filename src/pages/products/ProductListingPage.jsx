import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { productApi } from '../../services/api/productApi';
import ProductCard from '../../components/products/ProductCard';
import ProductFilterBar from '../../components/products/ProductFilterBar';
import Pagination from '../../components/products/Pagination';

// FIX #5: Page size set to the spec's documented default of 20.
// If a smaller page size is needed for demo/dev purposes, change this constant
// and add a comment explaining why.
const DEFAULT_PRODUCT_LIMIT = 20;

export default function ProductListingPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  // FIX #10: retryTrigger counter forces a re-fetch when incremented,
  // even when searchParams haven't changed — ensures the Retry button always works.
  const [retryTrigger, setRetryTrigger] = useState(0);
  
  // Pagination details
  const [pagination, setPagination] = useState({
    page: 1,
    limit: DEFAULT_PRODUCT_LIMIT,
    totalCount: 0,
    totalPages: 1
  });

  // Extract filters from URL Search Params so reload preserves filters
  const filters = {
    category: searchParams.get('category') || '',
    min_price: searchParams.get('min_price') || '',
    max_price: searchParams.get('max_price') || '',
    tags: searchParams.get('tags') || '',
    featured: searchParams.get('featured') === 'true',
    sort: searchParams.get('sort') || 'newest',
    page: parseInt(searchParams.get('page')) || 1
  };

  useEffect(() => {
    async function loadProducts() {
      setLoading(true);
      setError(null);
      try {
        const queryParams = {
          ...filters,
          limit: pagination.limit
        };
        const response = await productApi.fetchProducts(queryParams);
        // FIX #2: Both mock and live API now return normalized shape:
        // { products, totalCount, page, limit, totalPages }
        setProducts(response.products);
        setPagination({
          page: response.page,
          limit: response.limit,
          totalCount: response.totalCount,
          totalPages: response.totalPages
        });
      } catch (err) {
        setError(err.message || 'An error occurred while fetching products.');
      } finally {
        setLoading(false);
      }
    }

    loadProducts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams, retryTrigger]); // FIX #10: retryTrigger in deps ensures Retry always re-fetches

  const handleFilterChange = (key, value) => {
    const newParams = new URLSearchParams(searchParams);
    
    // Always reset page to 1 when filters change
    newParams.set('page', '1');

    if (value === undefined || value === null || value === '' || value === false) {
      newParams.delete(key);
    } else {
      newParams.set(key, value.toString());
    }
    
    setSearchParams(newParams);
  };

  const handlePageChange = (newPage) => {
    const newParams = new URLSearchParams(searchParams);
    newParams.set('page', newPage.toString());
    setSearchParams(newParams);
    
    // Smooth scroll to top of grid
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleClearFilters = () => {
    setSearchParams(new URLSearchParams());
  };

  return (
    <div className="catalog-page fade-in">
      <div className="catalog-hero">
        <h1 className="catalog-title">Explore Custom Creations</h1>
        <p className="catalog-subtitle">Personalize your gear with next-gen AI preview interfaces.</p>
      </div>

      <div className="listing-layout">
        {/* Left Filters */}
        <ProductFilterBar 
          filters={filters} 
          onFilterChange={handleFilterChange} 
          onClearFilters={handleClearFilters}
          products={products} /* FIX #8: pass loaded products for tag derivation */
        />

        {/* Right Content Area */}
        <div className="catalog-results">
          {error && (
            <div className="error-panel glass-panel">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="error-icon">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
              </svg>
              <h3>Failed to Load Products</h3>
              <p>{error}</p>
              {/* FIX #10: onClick increments retryTrigger to force state change and re-fetch */}
              <button className="retry-btn" onClick={() => setRetryTrigger(prev => prev + 1)}>
                Retry Fetch
              </button>
            </div>
          )}

          {!error && loading && (
            <div className="products-grid">
              {[...Array(6)].map((_, idx) => (
                <div key={idx} className="product-card glass-panel">
                  <div className="skeleton skeleton-image"></div>
                  <div className="card-details">
                    <div className="skeleton skeleton-title"></div>
                    <div className="skeleton skeleton-price"></div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {!error && !loading && products.length === 0 && (
            <div className="empty-panel glass-panel">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="empty-icon">
                <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 10.5V6a3.75 3.75 0 10-7.5 0v4.5m11.356-1.993l1.263 12c.07.665-.45 1.243-1.119 1.243H4.25a1.125 1.125 0 01-1.12-1.243l1.264-12A1.125 1.125 0 015.513 7.5h12.974c.576 0 1.059.435 1.119 1.007zM8.625 10.5a.375.375 0 11-.75 0 .375.375 0 01.75 0zm7.5 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z" />
              </svg>
              <h3>No Products Found</h3>
              <p>Try clearing some filters or narrowing down your search parameters.</p>
              <button className="clear-filters-btn active" onClick={handleClearFilters}>
                Clear All Filters
              </button>
            </div>
          )}

          {!error && !loading && products.length > 0 && (
            <>
              <div className="products-grid">
                {products.map(prod => (
                  <ProductCard key={prod._id} product={prod} />
                ))}
              </div>
              <Pagination 
                currentPage={pagination.page} 
                totalPages={pagination.totalPages} 
                onPageChange={handlePageChange} 
              />
            </>
          )}
        </div>
      </div>
    </div>
  );
}

import React, { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { productApi } from '../../services/api/productApi';
import ProductCard from '../../components/products/ProductCard';
import Pagination from '../../components/products/Pagination';

// FIX #5: Page size set to the spec's documented default of 20.
const DEFAULT_PRODUCT_LIMIT = 20;

export default function SearchResultsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const query = searchParams.get('q') || '';
  
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [validationError, setValidationError] = useState(null);
  // FIX #10: retryTrigger counter forces a re-fetch when incremented
  const [retryTrigger, setRetryTrigger] = useState(0);

  // Pagination details
  const [pagination, setPagination] = useState({
    page: 1,
    limit: DEFAULT_PRODUCT_LIMIT,
    totalCount: 0,
    totalPages: 1
  });

  const sort = searchParams.get('sort') || 'newest';
  const page = parseInt(searchParams.get('page')) || 1;

  useEffect(() => {
    // Client-side block/validate for queries under 2 characters
    if (!query) {
      setProducts([]);
      setValidationError('Please enter a search query.');
      return;
    }

    if (query.trim().length < 2) {
      setProducts([]);
      setValidationError('Search query must be at least 2 characters.');
      return;
    }

    setValidationError(null);

    async function executeSearch() {
      setLoading(true);
      setError(null);
      try {
        const response = await productApi.searchProducts(query, {
          sort,
          page,
          limit: pagination.limit
        });
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
        setError(err.message || 'An error occurred during search.');
      } finally {
        setLoading(false);
      }
    }

    executeSearch();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [query, sort, page, retryTrigger]); // FIX #10: retryTrigger ensures Retry always re-fetches

  const handleSortChange = (e) => {
    const newParams = new URLSearchParams(searchParams);
    newParams.set('sort', e.target.value);
    newParams.set('page', '1');
    setSearchParams(newParams);
  };

  const handlePageChange = (newPage) => {
    const newParams = new URLSearchParams(searchParams);
    newParams.set('page', newPage.toString());
    setSearchParams(newParams);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="search-page fade-in">
      <div className="search-header-row">
        <Link to="/" className="back-link">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" width="16" height="16">
            <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" />
          </svg>
          <span>Back to Catalog</span>
        </Link>
        
        <h1 className="search-title">
          {query ? `Search Results for "${query}"` : 'Product Search'}
        </h1>
      </div>

      {validationError && (
        <div className="error-panel glass-panel text-center">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="error-icon">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
          </svg>
          <h3>Search Query Blocked</h3>
          <p>{validationError}</p>
        </div>
      )}

      {error && !validationError && (
        <div className="error-panel glass-panel">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="error-icon">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
          </svg>
          <h3>Search Request Failed</h3>
          <p>{error}</p>
          {/* FIX #10: onClick increments retryTrigger to force state change and re-fetch */}
          <button className="retry-btn" onClick={() => setRetryTrigger(prev => prev + 1)}>
            Retry Fetch
          </button>
        </div>
      )}

      {loading && !validationError && !error && (
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

      {!loading && !validationError && !error && (
        <>
          {products.length === 0 ? (
            <div className="empty-panel glass-panel text-center">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="empty-icon">
                <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
              </svg>
              <h3>No Matches Found</h3>
              <p>We couldn't find any products matching "{query}". Check spelling or try other keywords.</p>
              <div className="empty-actions">
                <Link to="/" className="action-btn buy-btn">
                  Back to Catalog
                </Link>
              </div>
            </div>
          ) : (
            <div className="search-results-container">
              <div className="search-actions-row">
                <div className="results-counter">
                  Showing {products.length} of {pagination.totalCount} results
                </div>
                <div className="form-group sort-group">
                  <label htmlFor="search-sort" className="form-label inline">Sort: </label>
                  <select 
                    id="search-sort"
                    className="form-select inline"
                    value={sort}
                    onChange={handleSortChange}
                  >
                    <option value="newest">Newest</option>
                    <option value="price_asc">Price: Low to High</option>
                    <option value="price_desc">Price: High to Low</option>
                    <option value="popular">Popularity</option>
                  </select>
                </div>
              </div>

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
            </div>
          )}
        </>
      )}
    </div>
  );
}

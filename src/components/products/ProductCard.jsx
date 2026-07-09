import React from 'react';
import { Link } from 'react-router-dom';

/**
 * ProductCard — Public catalog list-view card component.
 *
 * FIX #2: Removed all branching based on `product.type`.
 * The `type` field is NOT part of the list-view API response (the backend
 * projects it out in GET /api/products), so the card must render identically
 * regardless of product type. Uses a single consistent CTA button ("View Product")
 * and no type-based badge.
 */
export default function ProductCard({ product }) {
  const {
    title,
    slug,
    thumbnail,
    base_price,
    stock_status,
    rating_avg,
    is_featured
    // FIX #2: `type` removed from destructuring — not available in list view
  } = product;

  const isOutOfStock = stock_status === 'out_of_stock';

  // Helper to render rating stars
  const renderStars = (rating) => {
    const stars = [];
    const floor = Math.floor(rating);
    for (let i = 1; i <= 5; i++) {
      if (i <= floor) {
        stars.push(<span key={i} className="star filled">★</span>);
      } else if (i - rating < 1) {
        stars.push(<span key={i} className="star half">★</span>); // Can styled in CSS as partial gradient or color
      } else {
        stars.push(<span key={i} className="star empty">☆</span>);
      }
    }
    return stars;
  };

  return (
    <div className={`product-card glass-panel fade-in ${isOutOfStock ? 'out-of-stock-card' : ''}`}>
      <Link to={`/products/${slug}`} className="card-image-link">
        <div className="card-image-wrapper">
          <img 
            src={thumbnail || 'https://images.unsplash.com/photo-1531403009284-440f080d1e12?auto=format&fit=crop&q=80&w=400'} 
            alt={title} 
            className="product-thumbnail"
            loading="lazy"
          />
          {isOutOfStock && <div className="out-of-stock-overlay">Out of Stock</div>}
          
          {/* FIX #2: Only show the "Featured" badge. Removed type-based badges
              (Fully Custom / Pre-Designed) — `type` is not in list-view response. */}
          <div className="card-badges">
            {is_featured && <span className="badge badge-featured">Featured</span>}
          </div>
        </div>
      </Link>

      <div className="card-details">
        <span className="card-category-slug">{product.category_slug}</span>
        
        <Link to={`/products/${slug}`}>
          <h3 className="product-card-title">{title}</h3>
        </Link>

        <div className="product-rating">
          <div className="stars-wrapper">{renderStars(rating_avg)}</div>
          <span className="rating-number">{rating_avg.toFixed(1)}</span>
        </div>

        <div className="card-footer">
          <div className="price-tag">
            <span className="price-currency">₹</span>
            <span className="price-value">{base_price.toFixed(2)}</span>
          </div>

          {/* FIX #2: Single consistent CTA button for all products — no type branching */}
          <Link 
            to={`/products/${slug}`} 
            className={`action-btn buy-btn ${isOutOfStock ? 'disabled' : ''}`}
          >
            <span>View Product</span>
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" width="14" height="14">
              <path strokeLinecap="round" strokeLinejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" />
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </Link>
        </div>
      </div>
    </div>
  );
}

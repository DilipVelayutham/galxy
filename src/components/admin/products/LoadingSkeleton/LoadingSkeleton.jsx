import React from 'react';
import './LoadingSkeleton.css';

/**
 * LoadingSkeleton - Animated placeholder shown while products are loading
 * Mimics the product table layout for a smooth loading experience
 */
const LoadingSkeleton = ({ rows = 5 }) => {
  return (
    <div className="skeleton-container">
      {/* Table header skeleton */}
      <div className="skeleton-header">
        {[...Array(7)].map((_, i) => (
          <div key={i} className="skeleton-header-cell">
            <div className="skeleton-pulse skeleton-text-sm" />
          </div>
        ))}
      </div>

      {/* Table rows skeleton */}
      {[...Array(rows)].map((_, rowIndex) => (
        <div key={rowIndex} className="skeleton-row" style={{ animationDelay: `${rowIndex * 0.08}s` }}>
          <div className="skeleton-cell">
            <div className="skeleton-pulse skeleton-image" />
          </div>
          <div className="skeleton-cell">
            <div className="skeleton-pulse skeleton-text-md" />
            <div className="skeleton-pulse skeleton-text-sm" style={{ width: '60%', marginTop: '8px' }} />
          </div>
          <div className="skeleton-cell">
            <div className="skeleton-pulse skeleton-badge" />
          </div>
          <div className="skeleton-cell">
            <div className="skeleton-pulse skeleton-text-sm" style={{ width: '50%' }} />
          </div>
          <div className="skeleton-cell">
            <div className="skeleton-pulse skeleton-badge" />
          </div>
          <div className="skeleton-cell">
            <div className="skeleton-pulse skeleton-toggle" />
          </div>
          <div className="skeleton-cell skeleton-actions">
            <div className="skeleton-pulse skeleton-action-btn" />
            <div className="skeleton-pulse skeleton-action-btn" />
          </div>
        </div>
      ))}
    </div>
  );
};

export default LoadingSkeleton;

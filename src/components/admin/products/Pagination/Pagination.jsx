import React from 'react';
import { FiChevronLeft, FiChevronRight, FiChevronsLeft, FiChevronsRight } from 'react-icons/fi';
import './Pagination.css';

/**
 * Pagination - Reusable pagination component
 * Features page numbers, prev/next, first/last, and page size selector
 */
const Pagination = ({
  page,
  totalPages,
  total,
  limit,
  hasNextPage,
  hasPrevPage,
  onPageChange,
  onPageSizeChange,
  pageSizeOptions = [5, 10, 20, 50],
}) => {
  /**
   * Generate array of page numbers to display
   * Shows current page with neighbors and ellipsis
   */
  const getPageNumbers = () => {
    const pages = [];
    const maxVisible = 5;

    if (totalPages <= maxVisible) {
      for (let i = 1; i <= totalPages; i++) pages.push(i);
    } else {
      // Always show first page
      pages.push(1);

      let start = Math.max(2, page - 1);
      let end = Math.min(totalPages - 1, page + 1);

      // Adjust range if at edges
      if (page <= 3) {
        end = Math.min(4, totalPages - 1);
      }
      if (page >= totalPages - 2) {
        start = Math.max(totalPages - 3, 2);
      }

      // Add ellipsis before range
      if (start > 2) pages.push('...');

      // Add range pages
      for (let i = start; i <= end; i++) pages.push(i);

      // Add ellipsis after range
      if (end < totalPages - 1) pages.push('...');

      // Always show last page
      if (totalPages > 1) pages.push(totalPages);
    }

    return pages;
  };

  // Calculate display range
  const startItem = (page - 1) * limit + 1;
  const endItem = Math.min(page * limit, total);

  if (totalPages <= 0) return null;

  return (
    <div className="pagination-container">
      {/* Results info */}
      <div className="pagination-info">
        <span className="pagination-results">
          Showing <strong>{startItem}</strong> – <strong>{endItem}</strong> of{' '}
          <strong>{total}</strong> products
        </span>
      </div>

      {/* Page navigation */}
      <div className="pagination-controls">
        {/* First page */}
        <button
          className="pagination-btn pagination-btn-nav"
          onClick={() => onPageChange(1)}
          disabled={!hasPrevPage}
          title="First page"
          aria-label="Go to first page"
        >
          <FiChevronsLeft />
        </button>

        {/* Previous page */}
        <button
          className="pagination-btn pagination-btn-nav"
          onClick={() => onPageChange(page - 1)}
          disabled={!hasPrevPage}
          title="Previous page"
          aria-label="Go to previous page"
        >
          <FiChevronLeft />
        </button>

        {/* Page numbers */}
        <div className="pagination-pages">
          {getPageNumbers().map((pageNum, index) =>
            pageNum === '...' ? (
              <span key={`ellipsis-${index}`} className="pagination-ellipsis">
                …
              </span>
            ) : (
              <button
                key={pageNum}
                className={`pagination-btn pagination-btn-page ${pageNum === page ? 'active' : ''}`}
                onClick={() => onPageChange(pageNum)}
                aria-label={`Page ${pageNum}`}
                aria-current={pageNum === page ? 'page' : undefined}
              >
                {pageNum}
              </button>
            )
          )}
        </div>

        {/* Next page */}
        <button
          className="pagination-btn pagination-btn-nav"
          onClick={() => onPageChange(page + 1)}
          disabled={!hasNextPage}
          title="Next page"
          aria-label="Go to next page"
        >
          <FiChevronRight />
        </button>

        {/* Last page */}
        <button
          className="pagination-btn pagination-btn-nav"
          onClick={() => onPageChange(totalPages)}
          disabled={!hasNextPage}
          title="Last page"
          aria-label="Go to last page"
        >
          <FiChevronsRight />
        </button>
      </div>

      {/* Page size selector */}
      <div className="pagination-size">
        <label htmlFor="page-size" className="pagination-size-label">Rows:</label>
        <select
          id="page-size"
          className="pagination-size-select"
          value={limit}
          onChange={(e) => onPageSizeChange(Number(e.target.value))}
        >
          {pageSizeOptions.map((size) => (
            <option key={size} value={size}>
              {size}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
};

export default Pagination;

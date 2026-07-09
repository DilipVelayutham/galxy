import React, { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { FiSearch, FiFilter, FiX, FiRefreshCw } from 'react-icons/fi';
import { STOCK_STATUS_OPTIONS } from '../../../../utils/constants';
import { debounce } from '../../../../utils/helpers';
import './ProductFilters.css';

/**
 * ProductFilters - Filter bar for the product listing
 * Includes search, category, stock status, and active status filters.
 * Categories are passed in from a real categories fetch (useCategories),
 * not a hard-coded list, and the category filter now operates on
 * category_id to match the API contract.
 */
const ProductFilters = ({ filters, categories = [], onFilterChange }) => {
  const [searchValue, setSearchValue] = useState(filters.search || '');
  const [showFilters, setShowFilters] = useState(false);

  // Debounced search to avoid excessive API calls
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const debouncedSearch = useCallback(
    debounce((value) => {
      onFilterChange({ search: value });
    }, 400),
    [onFilterChange]
  );

  // Handle search input change
  const handleSearchChange = (e) => {
    const value = e.target.value;
    setSearchValue(value);
    debouncedSearch(value);
  };

  // Clear search
  const clearSearch = () => {
    setSearchValue('');
    onFilterChange({ search: '' });
  };

  // Handle filter change
  const handleFilterChange = (key, value) => {
    onFilterChange({ [key]: value });
  };

  // Reset all filters
  const resetFilters = () => {
    setSearchValue('');
    onFilterChange({
      search: '',
      category_id: '',
      stock_status: '',
      is_active: '',
    });
  };

  // Check if any filter is active
  const hasActiveFilters =
    filters.search || filters.category_id || filters.stock_status || filters.is_active !== '';

  return (
    <div className="product-filters">
      {/* Search Bar */}
      <div className="filters-search-row">
        <div className="search-input-wrapper">
          <FiSearch className="search-icon" />
          <input
            type="text"
            className="search-input"
            placeholder="Search products by name or tags..."
            value={searchValue}
            onChange={handleSearchChange}
            aria-label="Search products"
          />
          {searchValue && (
            <button className="search-clear" onClick={clearSearch} aria-label="Clear search">
              <FiX />
            </button>
          )}
        </div>

        <button
          className={`filter-toggle-btn ${showFilters ? 'active' : ''}`}
          onClick={() => setShowFilters(!showFilters)}
          aria-label="Toggle filters"
        >
          <FiFilter />
          <span>Filters</span>
          {hasActiveFilters && <span className="filter-badge" />}
        </button>

        {hasActiveFilters && (
          <button className="filter-reset-btn" onClick={resetFilters} aria-label="Reset all filters">
            <FiRefreshCw />
            <span>Reset</span>
          </button>
        )}
      </div>

      {/* Filter Dropdowns */}
      {showFilters && (
        <motion.div
          className="filters-dropdown-row"
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          transition={{ duration: 0.25 }}
        >
          {/* Category Filter */}
          <div className="filter-group">
            <label className="filter-label">Category</label>
            <select
              className="filter-select"
              value={filters.category_id}
              onChange={(e) => handleFilterChange('category_id', e.target.value)}
            >
              <option value="">All Categories</option>
              {categories.map((cat) => (
                <option key={cat._id} value={cat._id}>
                  {cat.name}
                </option>
              ))}
            </select>
          </div>

          {/* Stock Status Filter */}
          <div className="filter-group">
            <label className="filter-label">Stock Status</label>
            <select
              className="filter-select"
              value={filters.stock_status}
              onChange={(e) => handleFilterChange('stock_status', e.target.value)}
            >
              <option value="">All Statuses</option>
              {STOCK_STATUS_OPTIONS.map((status) => (
                <option key={status.value} value={status.value}>
                  {status.label}
                </option>
              ))}
            </select>
          </div>

          {/* Active Status Filter */}
          <div className="filter-group">
            <label className="filter-label">Status</label>
            <select
              className="filter-select"
              value={filters.is_active}
              onChange={(e) => handleFilterChange('is_active', e.target.value)}
            >
              <option value="">All</option>
              <option value="true">Active</option>
              <option value="false">Inactive</option>
            </select>
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default ProductFilters;

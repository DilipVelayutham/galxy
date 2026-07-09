import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { FiPlus, FiPackage, FiAlertTriangle, FiRefreshCw } from 'react-icons/fi';
import useProducts from '../../../hooks/useProducts';
import useCategories from '../../../hooks/useCategories';
import ProductTable from '../../../components/admin/products/ProductTable/ProductTable';
import ProductFilters from '../../../components/admin/products/ProductFilters/ProductFilters';
import Pagination from '../../../components/admin/products/Pagination/Pagination';
import LoadingSkeleton from '../../../components/admin/products/LoadingSkeleton/LoadingSkeleton';
import ImageManager from '../../../components/admin/products/ImageManager/ImageManager';
import './AdminProductListPage.css';

/**
 * AdminProductListPage - Main product listing page
 * Features product table, search/filters, pagination, and image management modal
 */
const AdminProductListPage = () => {
  const navigate = useNavigate();
  const {
    products,
    loading,
    error,
    pagination,
    filters,
    updateFilters,
    changePage,
    changePageSize,
    toggleProductStatus,
    refresh,
  } = useProducts();
  const { categories } = useCategories();

  // Image manager modal state
  const [imageManagerProduct, setImageManagerProduct] = useState(null);

  const goToCreateProduct = () => navigate('/admin/products/new/edit');

  const hasActiveFilters = !!(
    filters.search ||
    filters.category_id ||
    filters.stock_status ||
    filters.is_active !== ''
  );

  return (
    <div className="admin-products-page">
      {/* Page Header */}
      <motion.div
        className="page-header"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <div className="page-header-left">
          <h1 className="page-title">Products</h1>
          <p className="page-subtitle">
            Manage your product catalog &middot; {pagination.total} total products
          </p>
        </div>
        <div className="page-header-right">
          {/* Uses React Router's navigate() instead of window.location.href
              so this stays an in-app SPA navigation (no full page reload). */}
          <button className="btn-add-product" onClick={goToCreateProduct}>
            <FiPlus />
            <span>Add Product</span>
          </button>
        </div>
      </motion.div>

      {/* Filters */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.1 }}
      >
        <ProductFilters filters={filters} categories={categories} onFilterChange={updateFilters} />
      </motion.div>

      {/* Product Table Card */}
      <motion.div
        className="products-card"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.2 }}
      >
        {/* Loading State */}
        {loading && <LoadingSkeleton rows={pagination.limit} />}

        {/* Error State */}
        {!loading && error && (
          <div className="state-container error-state">
            <div className="state-icon-wrapper error">
              <FiAlertTriangle />
            </div>
            <h3 className="state-title">Failed to Load Products</h3>
            <p className="state-message">{error}</p>
            <button className="state-action-btn" onClick={refresh}>
              <FiRefreshCw />
              <span>Try Again</span>
            </button>
          </div>
        )}

        {/* Empty State */}
        {!loading && !error && products.length === 0 && (
          <div className="state-container empty-state">
            <div className="state-icon-wrapper">
              <FiPackage />
            </div>
            <h3 className="state-title">No Products Found</h3>
            <p className="state-message">
              {hasActiveFilters
                ? 'Try adjusting your filters or search terms'
                : 'Get started by adding your first product'}
            </p>
            {!hasActiveFilters && (
              <button className="state-action-btn primary" onClick={goToCreateProduct}>
                <FiPlus />
                <span>Add Product</span>
              </button>
            )}
          </div>
        )}

        {/* Product Table */}
        {!loading && !error && products.length > 0 && (
          <>
            <ProductTable
              products={products}
              categories={categories}
              onToggleStatus={toggleProductStatus}
              onManageImages={(product) => setImageManagerProduct(product)}
            />
            <Pagination
              page={pagination.page}
              totalPages={pagination.totalPages}
              total={pagination.total}
              limit={pagination.limit}
              hasNextPage={pagination.hasNextPage}
              hasPrevPage={pagination.hasPrevPage}
              onPageChange={changePage}
              onPageSizeChange={changePageSize}
            />
          </>
        )}
      </motion.div>

      {/* Image Manager Modal */}
      <AnimatePresence>
        {imageManagerProduct && (
          <ImageManager
            product={imageManagerProduct}
            onClose={() => setImageManagerProduct(null)}
          />
        )}
      </AnimatePresence>
    </div>
  );
};

export default AdminProductListPage;

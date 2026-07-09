import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiPlus, FiPackage, FiAlertTriangle, FiRefreshCw } from 'react-icons/fi';
import useProducts from '../../../hooks/useProducts';
import ProductTable from '../../../components/admin/products/ProductTable/ProductTable';
import ProductFilters from '../../../components/admin/products/ProductFilters/ProductFilters';
import Pagination from '../../../components/admin/products/Pagination/Pagination';
import LoadingSkeleton from '../../../components/admin/products/LoadingSkeleton/LoadingSkeleton';
import ImageManager from '../../../components/admin/products/ImageManager/ImageManager';
import './AdminProducts.css';

/**
 * AdminProducts - Main product listing page
 * Features product table, search/filters, pagination, and image management modal
 */
const AdminProducts = () => {
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
    deleteProduct,
    refresh,
  } = useProducts();

  // Image manager modal state
  const [imageManagerProduct, setImageManagerProduct] = useState(null);

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
          <button
            className="btn-add-product"
            onClick={() => (window.location.href = '/admin/products/new/edit')}
          >
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
        <ProductFilters filters={filters} onFilterChange={updateFilters} />
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
              {filters.search ||
              filters.category ||
              filters.stockStatus ||
              filters.isActive !== ''
                ? 'Try adjusting your filters or search terms'
                : 'Get started by adding your first product'}
            </p>
            {!(filters.search || filters.category || filters.stockStatus) && (
              <button className="state-action-btn primary">
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
              onToggleStatus={toggleProductStatus}
              onDelete={deleteProduct}
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

export default AdminProducts;

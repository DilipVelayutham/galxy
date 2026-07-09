import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  FiEdit2,
  FiToggleLeft,
  FiToggleRight,
  FiImage,
  FiStar,
  FiAlertTriangle,
} from 'react-icons/fi';
import { formatCurrency, truncateText, getStockStatusInfo } from '../../../../utils/helpers';
import './ProductTable.css';

/**
 * ProductTable - Main product listing table
 * Displays products in a responsive table with actions.
 *
 * NOTE: there is intentionally only ONE removal action -- the Active/Inactive
 * toggle, which IS the soft delete/restore the API contract describes. A
 * separate "Delete" action (previously present here, worded as permanent)
 * contradicted that soft-delete design and misled admins about
 * reversibility, so it has been removed rather than just re-labeled.
 */
const ProductTable = ({ products, categories = [], onToggleStatus, onManageImages }) => {
  const navigate = useNavigate();
  const [confirmAction, setConfirmAction] = useState(null);

  const getCategoryName = (categoryId) => {
    const category = categories.find((c) => c._id === categoryId);
    return category ? category.name : 'Uncategorized';
  };

  // Handle edit navigation
  const handleEdit = (productId) => {
    navigate(`/admin/products/${productId}/edit`);
  };

  // Handle deactivate/activate with confirmation. Shows a soft warning
  // (not a hard block) if the product being activated has zero images.
  const handleToggleStatus = (product) => {
    const aboutToActivate = !product.is_active;
    const hasNoImages = !product.images || product.images.length === 0;

    setConfirmAction({
      product,
      message: `${aboutToActivate ? 'Activate' : 'Deactivate'} "${product.title}"?`,
      showZeroImagesWarning: aboutToActivate && hasNoImages,
    });
  };

  // Confirm action execution
  const executeConfirmedAction = () => {
    if (!confirmAction) return;
    onToggleStatus(confirmAction.product._id, confirmAction.product.is_active);
    setConfirmAction(null);
  };

  // Render star rating
  const renderRating = (avg, count) => {
    return (
      <div className="rating-display">
        <FiStar className="rating-star" />
        <span className="rating-value">{avg?.toFixed(1) || '0.0'}</span>
        <span className="rating-count">({count || 0})</span>
      </div>
    );
  };

  // Get thumbnail image for a product
  const getThumbnail = (product) => {
    if (!product.images || product.images.length === 0) return null;
    const thumb = product.images.find((img) => img.isThumbnail) || product.images[0];
    return thumb.url;
  };

  return (
    <>
      <div className="product-table-wrapper">
        <table className="product-table">
          <thead>
            <tr>
              <th className="th-image">Image</th>
              <th className="th-name">Product Name</th>
              <th className="th-category">Category</th>
              <th className="th-price">Price</th>
              <th className="th-stock">Stock</th>
              <th className="th-status">Status</th>
              <th className="th-rating">Rating</th>
              <th className="th-actions">Actions</th>
            </tr>
          </thead>
          <tbody>
            <AnimatePresence>
              {products.map((product, index) => {
                const stockInfo = getStockStatusInfo(product.stock_status);
                const thumbnail = getThumbnail(product);

                return (
                  <motion.tr
                    key={product._id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    transition={{ duration: 0.25, delay: index * 0.04 }}
                    className={`product-row ${!product.is_active ? 'inactive' : ''}`}
                  >
                    {/* Product Image */}
                    <td className="td-image">
                      <div className="product-image-cell">
                        {thumbnail ? (
                          <img
                            src={thumbnail}
                            alt={product.title}
                            className="product-thumbnail"
                            loading="lazy"
                          />
                        ) : (
                          <div className="product-no-image">
                            <FiImage />
                          </div>
                        )}
                      </div>
                    </td>

                    {/* Product Name */}
                    <td className="td-name">
                      <div className="product-name-cell">
                        <Link to={`/admin/products/${product._id}`} className="product-title-link">
                          <span className="product-title">{truncateText(product.title, 40)}</span>
                        </Link>
                        <span className="product-slug">{product.slug}</span>
                      </div>
                    </td>

                    {/* Category */}
                    <td className="td-category">
                      <span className="category-badge">{getCategoryName(product.category_id)}</span>
                    </td>

                    {/* Price */}
                    <td className="td-price">
                      <span className="price-value">{formatCurrency(product.base_price)}</span>
                    </td>

                    {/* Stock Status */}
                    <td className="td-stock">
                      <span
                        className="stock-badge"
                        style={{
                          color: stockInfo.color,
                          background: stockInfo.bg,
                          borderColor: stockInfo.color + '33',
                        }}
                      >
                        <span
                          className="stock-dot"
                          style={{ backgroundColor: stockInfo.color }}
                        />
                        {stockInfo.label}
                      </span>
                    </td>

                    {/* Active Status */}
                    <td className="td-status">
                      <button
                        className={`status-toggle ${product.is_active ? 'active' : ''}`}
                        onClick={() => handleToggleStatus(product)}
                        aria-label={product.is_active ? 'Deactivate product' : 'Activate product'}
                      >
                        {product.is_active ? <FiToggleRight /> : <FiToggleLeft />}
                        <span>{product.is_active ? 'Active' : 'Inactive'}</span>
                      </button>
                    </td>

                    {/* Rating */}
                    <td className="td-rating">
                      {renderRating(product.rating_avg, product.rating_count)}
                    </td>

                    {/* Actions */}
                    <td className="td-actions">
                      <div className="actions-cell">
                        <button
                          className="action-btn action-edit"
                          onClick={() => handleEdit(product._id)}
                          title="Edit product"
                          aria-label="Edit product"
                        >
                          <FiEdit2 />
                        </button>
                        <button
                          className="action-btn action-images"
                          onClick={() => onManageImages(product)}
                          title="Manage images"
                          aria-label="Manage images"
                        >
                          <FiImage />
                        </button>
                        <button
                          className="action-btn action-toggle"
                          onClick={() => handleToggleStatus(product)}
                          title={product.is_active ? 'Deactivate product' : 'Activate product'}
                          aria-label={product.is_active ? 'Deactivate product' : 'Activate product'}
                        >
                          {product.is_active ? <FiToggleLeft /> : <FiToggleRight />}
                        </button>
                      </div>
                    </td>
                  </motion.tr>
                );
              })}
            </AnimatePresence>
          </tbody>
        </table>
      </div>

      {/* Confirmation Dialog */}
      <AnimatePresence>
        {confirmAction && (
          <motion.div
            className="confirm-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setConfirmAction(null)}
          >
            <motion.div
              className="confirm-dialog"
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              onClick={(e) => e.stopPropagation()}
            >
              <h3 className="confirm-title">Confirm Action</h3>
              <p className="confirm-message">{confirmAction.message}</p>
              {confirmAction.showZeroImagesWarning && (
                <p className="confirm-warning">
                  <FiAlertTriangle />
                  This product has no images yet. It can still be activated, but consider adding
                  at least one image first.
                </p>
              )}
              <div className="confirm-actions">
                <button
                  className="confirm-btn confirm-cancel"
                  onClick={() => setConfirmAction(null)}
                >
                  Cancel
                </button>
                <button className="confirm-btn confirm-proceed" onClick={executeConfirmedAction}>
                  Confirm
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export default ProductTable;

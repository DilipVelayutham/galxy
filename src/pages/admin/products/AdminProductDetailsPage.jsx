import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';
import {
  FiArrowLeft,
  FiEdit2,
  FiImage,
  FiStar,
  FiTag,
  FiActivity,
  FiFileText,
  FiSettings,
  FiCalendar,
  FiAlertTriangle,
  FiTrendingUp,
} from 'react-icons/fi';
import adminProductApi from '../../../services/api/adminProductApi';
import useCategories from '../../../hooks/useCategories';
import { formatCurrency, getStockStatusInfo } from '../../../utils/helpers';
import ImageManager from '../../../components/admin/products/ImageManager/ImageManager';
import LoadingSkeleton from '../../../components/admin/products/LoadingSkeleton/LoadingSkeleton';
import './AdminProductDetailsPage.css';

/**
 * AdminProductDetailsPage - Read-only product details view
 * Features full specifications list, attribute schemas, image viewer, and analytics
 */
const AdminProductDetailsPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedImage, setSelectedImage] = useState(null);
  const [showImageManager, setShowImageManager] = useState(false);

  const { getCategoryById } = useCategories();

  const fetchProductDetails = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await adminProductApi.getProductById(id);
      if (result.success && result.data) {
        setProduct(result.data);
        // Set first thumbnail or first image as default selected image
        if (result.data.images && result.data.images.length > 0) {
          const thumb = result.data.images.find((img) => img.isThumbnail) || result.data.images[0];
          setSelectedImage(thumb);
        } else {
          setSelectedImage(null);
        }
      } else {
        throw new Error('Product details empty');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load product details.');
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchProductDetails();
  }, [fetchProductDetails]);

  if (loading) {
    return (
      <div className="product-details-page loading">
        <LoadingSkeleton rows={10} />
      </div>
    );
  }

  if (error || !product) {
    return (
      <div className="product-details-page error-state-container">
        <div className="error-card">
          <FiAlertTriangle className="error-icon" />
          <h2>Error Loading Product</h2>
          <p>{error || 'Product not found.'}</p>
          <button className="back-link-btn" onClick={() => navigate('/admin/products')}>
            <FiArrowLeft /> Back to List
          </button>
        </div>
      </div>
    );
  }

  const category = getCategoryById(product.category_id);
  const stockInfo = getStockStatusInfo(product.stock_status);
  const specifications = product.specifications || {};

  // Parse specifications text or dict
  const renderSpecs = () => {
    if (typeof specifications === 'string') {
      return (
        <div className="specs-text-block">
          {specifications.split('|').map((s, idx) => (
            <span key={idx} className="spec-tag">
              {s.trim()}
            </span>
          ))}
        </div>
      );
    }

    if (Object.keys(specifications).length === 0) {
      return <p className="no-specs-hint">No specifications provided.</p>;
    }

    return (
      <div className="specs-grid">
        {Object.entries(specifications).map(([key, val]) => (
          <div key={key} className="spec-item">
            <span className="spec-key">{key}</span>
            <span className="spec-val">{val}</span>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="product-details-page">
      {/* Header Navigation */}
      <div className="details-header">
        <button className="back-btn" onClick={() => navigate('/admin/products')}>
          <FiArrowLeft /> Back to Products
        </button>
        <div className="header-actions">
          <button className="action-btn manage-images-btn" onClick={() => setShowImageManager(true)}>
            <FiImage /> Manage Images
          </button>
          <Link to={`/admin/products/${product._id}/edit`} className="action-btn edit-btn">
            <FiEdit2 /> Edit Product
          </Link>
        </div>
      </div>

      <div className="details-container">
        {/* Left Column: Image Viewer */}
        <div className="details-gallery-card">
          <div className="main-display-wrapper">
            {selectedImage ? (
              <img
                src={selectedImage.url}
                alt={product.title}
                className="main-display-image"
              />
            ) : (
              <div className="main-display-empty">
                <FiImage />
                <span>No images uploaded</span>
              </div>
            )}
            {selectedImage?.isThumbnail && (
              <span className="gallery-thumbnail-badge">Main Thumbnail</span>
            )}
          </div>
          {product.images && product.images.length > 0 && (
            <div className="gallery-thumbnails">
              {product.images.map((img) => (
                <button
                  key={img._id}
                  className={`thumb-card ${selectedImage?._id === img._id ? 'active' : ''} ${
                    img.isThumbnail ? 'is-thumb' : ''
                  }`}
                  onClick={() => setSelectedImage(img)}
                >
                  <img src={img.url} alt="Thumbnail preview" />
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Right Column: Information Sheet */}
        <div className="details-info-sheet">
          <div className="info-section-header">
            <span className="info-type-badge">{product.type === 'pre_designed' ? 'Pre-Designed' : 'Fully Custom'}</span>
            <h1 className="info-title">{product.title}</h1>
            <span className="info-slug">Slug: {product.slug}</span>
          </div>

          {/* Pricing & Stock Card */}
          <div className="metrics-card">
            <div className="metric-box">
              <span className="metric-label">Base Price</span>
              <span className="metric-value">{formatCurrency(product.base_price)}</span>
            </div>
            <div className="metric-box">
              <span className="metric-label">Stock Status</span>
              <span
                className="stock-status-tag"
                style={{
                  color: stockInfo.color,
                  backgroundColor: stockInfo.bg,
                  borderColor: stockInfo.color + '33',
                }}
              >
                {stockInfo.label}
              </span>
            </div>
            <div className="metric-box">
              <span className="metric-label">Catalog Status</span>
              <span className={`status-tag ${product.is_active ? 'active' : 'inactive'}`}>
                {product.is_active ? 'Active' : 'Inactive'}
              </span>
            </div>
          </div>

          {/* Description */}
          <div className="info-card">
            <h3 className="card-section-title">
              <FiFileText /> Description
            </h3>
            <p className="description-content">
              {product.description || 'No description provided.'}
            </p>
          </div>

          {/* Category details & custom attributes */}
          <div className="info-card">
            <h3 className="card-section-title">
              <FiTag /> Category: {category?.name || product.category_slug || 'Uncategorized'}
            </h3>
            {product.default_attributes && Object.keys(product.default_attributes).length > 0 ? (
              <div className="attributes-grid">
                {Object.entries(product.default_attributes).map(([key, val]) => (
                  <div key={key} className="attribute-item">
                    <span className="attr-key">{key}</span>
                    <span className="attr-val">{val.toString()}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="no-attributes-hint">No category attributes configured.</p>
            )}
          </div>

          {/* Specs */}
          <div className="info-card">
            <h3 className="card-section-title">
              <FiSettings /> Specifications
            </h3>
            {renderSpecs()}
          </div>

          {/* Metadata Analytics */}
          <div className="info-card analytics-card">
            <h3 className="card-section-title">
              <FiActivity /> System Analytics
            </h3>
            <div className="analytics-grid">
              <div className="analytic-item">
                <FiTrendingUp className="icon" />
                <div>
                  <span className="num">{product.views}</span>
                  <span className="label">Total Views</span>
                </div>
              </div>
              <div className="analytic-item">
                <FiStar className="icon star" />
                <div>
                  <span className="num">{product.rating_avg?.toFixed(1) || '0.0'}</span>
                  <span className="label">{product.rating_count || 0} reviews</span>
                </div>
              </div>
              <div className="analytic-item date-item">
                <FiCalendar className="icon" />
                <div>
                  <span className="date-str">{product.created_at ? new Date(product.created_at).toLocaleDateString() : 'N/A'}</span>
                  <span className="label">Created At</span>
                </div>
              </div>
              <div className="analytic-item date-item">
                <FiCalendar className="icon" />
                <div>
                  <span className="date-str">{product.updated_at ? new Date(product.updated_at).toLocaleDateString() : 'N/A'}</span>
                  <span className="label">Last Updated</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Image Manager Modal integration */}
      <AnimatePresence>
        {showImageManager && (
          <ImageManager
            product={product}
            onClose={() => {
              setShowImageManager(false);
              fetchProductDetails(); // Reload changes made in ImageManager
            }}
          />
        )}
      </AnimatePresence>
    </div>
  );
};

export default AdminProductDetailsPage;

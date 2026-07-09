import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import useProductForm from '../../../hooks/useProductForm';
import ProductForm from '../../../components/admin/products/ProductForm/ProductForm';
import LoadingSkeleton from '../../../components/admin/products/LoadingSkeleton/LoadingSkeleton';
import './EditProduct.css';

/**
 * EditProduct - Product editing / creation page
 * Uses useProductForm hook for form state management
 * Supports both create (id="new") and edit modes
 */
const EditProduct = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  // Determine if creating new or editing existing
  const productId = id === 'new' ? null : id;

  const {
    register,
    handleSubmit,
    errors,
    isSubmitting,
    isEditMode,
    watchedTitle,
    fetchLoading,
  } = useProductForm(productId);

  // Show loading skeleton while fetching product data in edit mode
  if (fetchLoading) {
    return (
      <div className="edit-product-page">
        <div className="edit-product-loading">
          <div className="loading-header">
            <div
              className="skeleton-pulse"
              style={{ width: '200px', height: '32px', borderRadius: '8px' }}
            />
            <div
              className="skeleton-pulse"
              style={{
                width: '300px',
                height: '16px',
                borderRadius: '6px',
                marginTop: '8px',
              }}
            />
          </div>
          <LoadingSkeleton rows={6} />
        </div>
      </div>
    );
  }

  return (
    <div className="edit-product-page">
      <ProductForm
        register={register}
        errors={errors}
        isSubmitting={isSubmitting}
        isEditMode={isEditMode}
        watchedTitle={watchedTitle}
        onSubmit={handleSubmit}
        onCancel={() => navigate('/admin/products')}
      />
    </div>
  );
};

export default EditProduct;

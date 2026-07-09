import React from 'react';
import { motion } from 'framer-motion';
import {
  FiSave,
  FiArrowLeft,
  FiTag,
  FiType,
  FiDollarSign,
  FiFileText,
  FiList,
  FiHash,
  FiStar,
  FiBox,
  FiLink,
  FiInfo,
} from 'react-icons/fi';
import { PRODUCT_TYPES, STOCK_STATUS_OPTIONS } from '../../../../utils/constants';
import ValidationErrors from '../ValidationErrors/ValidationErrors';
import './ProductForm.css';

/**
 * ProductForm - Product create/edit form component
 * Uses React Hook Form for validation and state management.
 *
 * Field names match the documented snake_case API contract directly
 * (category_id, base_price, stock_status, is_featured, default_attributes,
 * type) so there is no separate camelCase<->snake_case mapping layer to
 * keep in sync with the backend.
 */
const ProductForm = ({
  register,
  errors,
  isSubmitting,
  isEditMode,
  watchedTitle,
  categories,
  selectedCategory,
  onSubmit,
  onCancel,
  onClear,
  setValue,
  watch,
  product,
}) => {
  // Character counter for title
  const titleLength = watchedTitle?.length || 0;
  const titleMaxLength = 120;
  const titleMinLength = 3;

  const attributeSchema = selectedCategory?.attribute_schema || [];

  return (
    <motion.form
      className="product-form"
      onSubmit={onSubmit}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      {/* Form Header */}
      <div className="form-header">
        <button type="button" className="back-btn" onClick={onCancel}>
          <FiArrowLeft />
          <span>Back to Products</span>
        </button>
        <h1 className="form-title">{isEditMode ? 'Edit Product' : 'Create Product'}</h1>
        <p className="form-subtitle">
          {isEditMode
            ? 'Update the product details below'
            : 'Fill in the details to add a new product'}
        </p>
      </div>

      {/* Main Form Grid */}
      <div className="form-grid">
        {/* ---- Left Column ---- */}
        <div className="form-column">
          {/* Category */}
          <div className="form-group">
            <label className="form-label">
              <FiTag className="label-icon" />
              Category <span className="required">*</span>
              {isEditMode && <span className="read-only-badge">Read Only</span>}
            </label>
            <select
              className={`form-select ${errors.category_id ? 'input-error' : ''}`}
              disabled={isEditMode}
              {...register('category_id', { required: 'Category is required' })}
            >
              <option value="">Select a category</option>
              {categories.map((cat) => (
                <option key={cat._id} value={cat._id}>
                  {cat.name}
                </option>
              ))}
            </select>
            {isEditMode && (
              <span className="form-hint">
                <FiInfo style={{ verticalAlign: 'middle', marginRight: 4 }} />
                To move this product to another category, deactivate and recreate it.
              </span>
            )}
            <ValidationErrors message={errors.category_id?.message} show={!!errors.category_id} />
          </div>

          {/* Title with Character Counter */}
          <div className="form-group">
            <label className="form-label">
              <FiType className="label-icon" />
              Title <span className="required">*</span>
            </label>
            <div className="input-with-counter">
              <input
                type="text"
                className={`form-input ${errors.title ? 'input-error' : ''}`}
                placeholder="Enter product title"
                {...register('title', {
                  required: 'Title is required',
                  minLength: {
                    value: titleMinLength,
                    message: `Title must be at least ${titleMinLength} characters`,
                  },
                  maxLength: {
                    value: titleMaxLength,
                    message: `Title cannot exceed ${titleMaxLength} characters`,
                  },
                })}
              />
              <span
                className={`char-counter ${
                  titleLength > titleMaxLength
                    ? 'over'
                    : titleLength >= titleMaxLength - 20
                    ? 'warning'
                    : ''
                }`}
              >
                {titleLength}/{titleMaxLength}
              </span>
            </div>
            <ValidationErrors message={errors.title?.message} show={!!errors.title} />
          </div>

          {/* Slug */}
          <div className="form-group">
            <label className="form-label">
              <FiLink className="label-icon" />
              Slug {isEditMode && <span className="read-only-badge">Read Only</span>}
            </label>
            <input
              type="text"
              className="form-input slug-input"
              placeholder="auto-generated-slug"
              readOnly={isEditMode}
              {...register('slug')}
            />
            <ValidationErrors message={errors.slug?.message} show={!!errors.slug} />
          </div>

          {/* Type */}
          <div className="form-group">
            <label className="form-label">
              <FiInfo className="label-icon" />
              Product Type {isEditMode && <span className="read-only-badge">Read Only</span>}
            </label>
            <div className="type-options-group">
              {PRODUCT_TYPES.map((t) => (
                <label
                  key={t.value}
                  className={`type-option-card ${isEditMode ? 'disabled' : ''}`}
                >
                  <input
                    type="radio"
                    value={t.value}
                    disabled={isEditMode}
                    {...register('type', { required: 'Product type is required' })}
                  />
                  <div className="type-option-content">
                    <span className="type-option-label">{t.label}</span>
                    <span className="type-option-desc">
                      {t.value === 'pre_designed'
                        ? 'Ready designs with fixed customizable attributes.'
                        : 'Fully personalized user-configured options.'}
                    </span>
                  </div>
                </label>
              ))}
            </div>
            <ValidationErrors message={errors.type?.message} show={!!errors.type} />
          </div>

          {/* Price */}
          <div className="form-group">
            <label className="form-label">
              <FiDollarSign className="label-icon" />
              Base Price (INR) <span className="required">*</span>
            </label>
            <input
              type="number"
              step="0.01"
              className={`form-input ${errors.base_price ? 'input-error' : ''}`}
              placeholder="0.00"
              {...register('base_price', {
                required: 'Base price is required',
                min: { value: 0.01, message: 'Price must be greater than 0' },
              })}
            />
            <ValidationErrors message={errors.base_price?.message} show={!!errors.base_price} />
          </div>

          {/* Description */}
          <div className="form-group">
            <label className="form-label">
              <FiFileText className="label-icon" />
              Description
            </label>
            <textarea
              className="form-textarea"
              placeholder="Describe the product details..."
              rows={4}
              {...register('description')}
            />
            <ValidationErrors message={errors.description?.message} show={!!errors.description} />
          </div>
        </div>

        {/* ---- Right Column ---- */}
        <div className="form-column">
          {/* Specifications */}
          <div className="form-group">
            <label className="form-label">
              <FiList className="label-icon" />
              Technical Specifications (JSDoc/Text format)
            </label>
            <textarea
              className="form-textarea specs-textarea"
              placeholder="e.g. Material: Flex LED Neon | Power: 12V Adapter | Life: 50,000 hrs"
              rows={4}
              {...register('specifications')}
            />
            <span className="form-hint">Format as Key: Value | Key: Value or simple text</span>
            <ValidationErrors message={errors.specifications?.message} show={!!errors.specifications} />
          </div>

          {/* Stock Status */}
          <div className="form-group">
            <label className="form-label">
              <FiBox className="label-icon" />
              Stock Status
            </label>
            <select className="form-select" {...register('stock_status')}>
              {STOCK_STATUS_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
            <ValidationErrors message={errors.stock_status?.message} show={!!errors.stock_status} />
          </div>

          {/* Category Attributes Schema-driven inputs */}
          <div className="form-group category-attributes-box">
            <label className="form-label">
              <FiHash className="label-icon" />
              Category Attributes ({selectedCategory?.name || 'No category selected'})
            </label>
            {!selectedCategory && (
              <div className="attributes-empty-state">
                Select a category to customize attributes.
              </div>
            )}
            {selectedCategory && attributeSchema.length === 0 && (
              <div className="attributes-empty-state">
                No custom attributes defined for this category.
              </div>
            )}
            <div className="attribute-schema-grid">
              {selectedCategory &&
                attributeSchema.map((attr) => {
                  const fieldName = `default_attributes.${attr.key}`;
                  const fieldError = errors.default_attributes?.[attr.key];

                  return (
                    <div key={attr.key} className="attribute-field">
                      <label className="attribute-label">{attr.label}</label>
                      {attr.type === 'select' ? (
                        <select className="form-select" {...register(fieldName)}>
                          <option value="">Select option</option>
                          {attr.options?.map((opt) => (
                            <option key={opt} value={opt}>
                              {opt}
                            </option>
                          ))}
                        </select>
                      ) : attr.type === 'number' || attr.type === 'slider' ? (
                        <input
                          type="number"
                          className="form-input"
                          min={attr.min}
                          max={attr.max}
                          {...register(fieldName, { valueAsNumber: true })}
                        />
                      ) : attr.type === 'toggle' ? (
                        <label className="toggle-switch" style={{ width: '48px', marginTop: '6px' }}>
                          <input type="checkbox" {...register(fieldName)} />
                          <span className="toggle-slider" />
                        </label>
                      ) : attr.type === 'color_swatch' ? (
                        <input
                          type="color"
                          className="form-input"
                          {...register(fieldName)}
                          style={{ height: '42px', padding: '4px', cursor: 'pointer' }}
                        />
                      ) : attr.type === 'image_swatch' ? (
                        <div className="image-swatch-picker-container">
                          <input
                            type="text"
                            className="form-input"
                            placeholder="Image URL"
                            {...register(fieldName)}
                          />
                          {( (attr.options && attr.options.length > 0) || (product?.images && product.images.length > 0) ) && (
                            <div className="image-swatch-options">
                              {attr.options?.map((opt) => {
                                const isSelected = watch?.(fieldName) === opt;
                                return (
                                  <button
                                    type="button"
                                    key={opt}
                                    className={`image-swatch-option ${isSelected ? 'selected' : ''}`}
                                    onClick={() => setValue?.(fieldName, opt, { shouldDirty: true })}
                                    title="Select predefined pattern/image"
                                  >
                                    <img src={opt} alt="Pattern swatch" />
                                  </button>
                                );
                              })}
                              {product?.images?.map((img) => {
                                const isSelected = watch?.(fieldName) === img.url;
                                return (
                                  <button
                                    type="button"
                                    key={img._id}
                                    className={`image-swatch-option ${isSelected ? 'selected' : ''}`}
                                    onClick={() => setValue?.(fieldName, img.url, { shouldDirty: true })}
                                    title="Use product image"
                                  >
                                    <img src={img.url} alt="Product image swatch" />
                                  </button>
                                );
                              })}
                            </div>
                          )}
                        </div>
                      ) : (
                        <input type="text" className="form-input" {...register(fieldName)} />
                      )}
                      <ValidationErrors message={fieldError?.message} show={!!fieldError} />
                    </div>
                  );
                })}
            </div>
          </div>

          {/* Tags */}
          <div className="form-group">
            <label className="form-label">
              <FiTag className="label-icon" />
              Tags
            </label>
            <input
              type="text"
              className="form-input"
              placeholder="Enter tags separated by commas"
              {...register('tags')}
            />
            <span className="form-hint">Separate tags with commas (e.g., wireless, premium, bluetooth)</span>
          </div>

          {/* Featured Toggle */}
          <div className="form-group">
            <label className="form-label">
              <FiStar className="label-icon" />
              Featured Product
            </label>
            <label className="toggle-switch">
              <input type="checkbox" {...register('is_featured')} />
              <span className="toggle-slider" />
              <span className="toggle-label">Mark as featured product</span>
            </label>
          </div>
        </div>
      </div>

      {/* Form Actions */}
      <div className="form-actions">
        {!isEditMode && (
          <button
            type="button"
            className="btn-secondary btn-clear"
            onClick={onClear}
            style={{ marginRight: 'auto' }}
          >
            Clear Form
          </button>
        )}
        <button type="button" className="btn-secondary" onClick={onCancel}>
          Cancel
        </button>
        <button
          type="submit"
          className="btn-primary"
          disabled={isSubmitting}
        >
          {isSubmitting ? (
            <>
              <span className="btn-spinner" />
              <span>Saving...</span>
            </>
          ) : (
            <>
              <FiSave />
              <span>{isEditMode ? 'Update Product' : 'Create Product'}</span>
            </>
          )}
        </button>
      </div>
    </motion.form>
  );
};

export default ProductForm;

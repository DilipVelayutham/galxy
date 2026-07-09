import { useState, useEffect, useCallback } from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import adminProductApi from '../services/api/adminProductApi';
import { mockProducts } from '../services/api/mockData';
import useCategories from './useCategories';
import { generateSlug } from '../utils/helpers';
import toast from 'react-hot-toast';

// Flag to toggle between mock data and real API
const USE_MOCK = false;

/**
 * useProductForm - Custom hook for product form state management
 * Handles form initialization, validation, and submission.
 *
 * Field names throughout (category_id, base_price, stock_status,
 * is_featured, default_attributes, type) match the snake_case API contract
 * directly, so there's no separate mapping layer to keep in sync with the
 * backend and no risk of sending camelCase keys it doesn't recognize.
 *
 * @param {string} productId - Product ID for edit mode (null for create)
 */
const useProductForm = (productId = null) => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [fetchLoading, setFetchLoading] = useState(!!productId);
  const [product, setProduct] = useState(null);

  const isEditMode = !!productId;
  const { categories, getCategoryById } = useCategories();

  // Initialize React Hook Form with validation
  const {
    register,
    handleSubmit,
    formState: { errors, isDirty, isSubmitting },
    reset,
    watch,
    setValue,
    setError,
    control,
    trigger,
  } = useForm({
    defaultValues: {
      category_id: '',
      title: '',
      slug: '',
      type: 'pre_designed',
      base_price: '',
      description: '',
      specifications: '',
      default_attributes: {},
      stock_status: 'in_stock',
      tags: '',
      is_featured: false,
    },
    mode: 'onChange',
  });

  // Watch title for slug auto-generation and character counter
  const watchedTitle = watch('title');
  const watchedCategoryId = watch('category_id');
  const selectedCategory = getCategoryById(watchedCategoryId);

  // Auto-generate slug from title (only in create mode)
  useEffect(() => {
    if (!isEditMode && watchedTitle) {
      setValue('slug', generateSlug(watchedTitle), { shouldDirty: false });
    }
  }, [watchedTitle, isEditMode, setValue]);

  /**
   * Fetch product data for edit mode
   */
  useEffect(() => {
    if (!productId) return;

    const fetchProduct = async () => {
      setFetchLoading(true);
      try {
        let productData;
        if (USE_MOCK) {
          await new Promise((resolve) => setTimeout(resolve, 500));
          productData = mockProducts.find((p) => p._id === productId);
          if (!productData) throw new Error('Product not found');
        } else {
          const result = await adminProductApi.getProductById(productId);
          productData = result.data;
        }

        setProduct(productData);

        // Populate form with fetched data
        reset({
          category_id: productData.category_id || '',
          title: productData.title || '',
          slug: productData.slug || '',
          type: productData.type || 'pre_designed',
          base_price: productData.base_price ?? '',
          description: productData.description || '',
          specifications: productData.specifications || '',
          default_attributes: productData.default_attributes || {},
          stock_status: productData.stock_status || 'in_stock',
          tags: Array.isArray(productData.tags) ? productData.tags.join(', ') : productData.tags || '',
          is_featured: productData.is_featured || false,
        });
      } catch (err) {
        toast.error('Failed to load product details');
        navigate('/admin/products');
      } finally {
        setFetchLoading(false);
      }
    };

    fetchProduct();
  }, [productId, reset, navigate]);

  /**
   * Submit handler for the product form
   */
  const onSubmit = useCallback(
    async (formData) => {
      setLoading(true);
      try {
        // Process tags from comma-separated string to array
        const processedData = {
          ...formData,
          base_price: parseFloat(formData.base_price),
          tags: formData.tags
            ? formData.tags.split(',').map((tag) => tag.trim()).filter(Boolean)
            : [],
        };

        if (USE_MOCK) {
          await new Promise((resolve) => setTimeout(resolve, 800));
          toast.success(
            isEditMode ? 'Product updated successfully!' : 'Product created successfully!'
          );
        } else if (isEditMode) {
          await adminProductApi.updateProduct(productId, processedData);
          toast.success('Product updated successfully!');
        } else {
          await adminProductApi.createProduct(processedData);
          toast.success('Product created successfully!');
        }

        navigate('/admin/products');
      } catch (err) {
        // Surface 400 field-level errors inline next to the offending
        // field (e.g. a bad default_attributes key) instead of only a
        // generic toast. Expects a backend shape like:
        //   { message: '...', errors: { base_price: 'must be positive', 'default_attributes.color': 'invalid option' } }
        const fieldErrors = err.response?.data?.errors;
        if (err.response?.status === 400 && fieldErrors && typeof fieldErrors === 'object') {
          Object.entries(fieldErrors).forEach(([field, message]) => {
            setError(field, { type: 'server', message });
          });
          toast.error('Please fix the highlighted fields');
        } else {
          const errorMessage =
            err.response?.data?.message || `Failed to ${isEditMode ? 'update' : 'create'} product`;
          toast.error(errorMessage);
        }
      } finally {
        setLoading(false);
      }
    },
    [isEditMode, productId, navigate, setError]
  );

  return {
    register,
    handleSubmit: handleSubmit(onSubmit),
    errors,
    isDirty,
    isSubmitting: isSubmitting || loading,
    watch,
    setValue,
    control,
    trigger,
    product,
    categories,
    selectedCategory,
    fetchLoading,
    isEditMode,
    watchedTitle,
    reset,
  };
};

export default useProductForm;

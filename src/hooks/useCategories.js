import { useState, useEffect, useCallback } from 'react';
import adminProductApi from '../services/api/adminProductApi';
import { getMockCategoriesResponse } from '../services/api/mockData';

// Flag to toggle between mock data and real API
const USE_MOCK = false;

/**
 * useCategories - Fetches real category documents (each with _id, name,
 * attribute_schema, accent_color, hero_image) instead of relying on a
 * hard-coded category name list. This is what lets ProductForm resolve
 * category_id -> attribute_schema for the structured default_attributes
 * inputs, and is required for the create/edit form to send a valid
 * category_id the backend actually recognizes.
 */
const useCategories = () => {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchCategories = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      let result;
      if (USE_MOCK) {
        await new Promise((resolve) => setTimeout(resolve, 300));
        result = getMockCategoriesResponse();
      } else {
        result = await adminProductApi.getCategories();
      }

      if (result.success) {
        setCategories(result.data.categories);
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to fetch categories');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCategories();
  }, [fetchCategories]);

  const getCategoryById = useCallback(
    (categoryId) => categories.find((c) => c._id === categoryId) || null,
    [categories]
  );

  return { categories, loading, error, getCategoryById, refresh: fetchCategories };
};

export default useCategories;

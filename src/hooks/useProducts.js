import { useState, useEffect, useCallback } from 'react';
import adminProductApi from '../services/api/adminProductApi';
import { getMockProductsResponse } from '../services/api/mockData';
import toast from 'react-hot-toast';

// Flag to toggle between mock data and real API
const USE_MOCK = false;

/**
 * useProducts - Custom hook for managing product list state
 * Handles fetching, filtering, pagination, and status toggling.
 *
 * NOTE: there is deliberately no separate "delete" action here. The API
 * contract's DELETE /api/admin/products/:id is a soft delete, and the
 * product-status toggle (toggleProductStatus) IS that soft delete/restore
 * action. A second, differently-worded "Delete" action would contradict
 * the soft-delete design and mislead admins about reversibility.
 */
const useProducts = () => {
  // Product list state
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Pagination state
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 10,
    total: 0,
    totalPages: 0,
    hasNextPage: false,
    hasPrevPage: false,
  });

  // Filter state
  const [filters, setFilters] = useState({
    search: '',
    category_id: '',
    stock_status: '',
    is_active: '',
  });

  /**
   * Fetch products with current filters and pagination
   */
  const fetchProducts = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const params = {
        page: pagination.page,
        limit: pagination.limit,
        ...filters,
      };

      // Remove empty filter values
      Object.keys(params).forEach((key) => {
        if (params[key] === '' || params[key] === null || params[key] === undefined) {
          delete params[key];
        }
      });

      let result;
      if (USE_MOCK) {
        // Simulate network delay
        await new Promise((resolve) => setTimeout(resolve, 600));
        result = getMockProductsResponse(params);
      } else {
        result = await adminProductApi.getProducts(params);
      }

      if (result.success) {
        setProducts(result.data.products);
        setPagination((prev) => ({
          ...prev,
          ...result.data.pagination,
        }));
      }
    } catch (err) {
      const errorMessage = err.response?.data?.message || 'Failed to fetch products';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [pagination.page, pagination.limit, filters]);

  // Fetch products when filters or page changes
  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  /**
   * Update filter values and reset to page 1
   */
  const updateFilters = useCallback((newFilters) => {
    setFilters((prev) => ({ ...prev, ...newFilters }));
    setPagination((prev) => ({ ...prev, page: 1 }));
  }, []);

  /**
   * Change page
   */
  const changePage = useCallback((newPage) => {
    setPagination((prev) => ({ ...prev, page: newPage }));
  }, []);

  /**
   * Change page size
   */
  const changePageSize = useCallback((newLimit) => {
    setPagination((prev) => ({ ...prev, limit: newLimit, page: 1 }));
  }, []);

  /**
   * Toggle product active status (this is the one and only soft-delete /
   * restore action -- see note above)
   */
  const toggleProductStatus = useCallback(
    async (productId, currentStatus) => {
      try {
        if (USE_MOCK) {
          // Simulate API call
          await new Promise((resolve) => setTimeout(resolve, 400));
          setProducts((prev) =>
            prev.map((p) => (p._id === productId ? { ...p, is_active: !currentStatus } : p))
          );
          toast.success(`Product ${!currentStatus ? 'activated' : 'deactivated'} successfully`);
        } else {
          await adminProductApi.toggleProductStatus(productId, !currentStatus);
          toast.success(`Product ${!currentStatus ? 'activated' : 'deactivated'} successfully`);
          fetchProducts();
        }
      } catch (err) {
        toast.error('Failed to update product status');
      }
    },
    [fetchProducts]
  );

  /**
   * Refresh the product list
   */
  const refresh = useCallback(() => {
    fetchProducts();
  }, [fetchProducts]);

  return {
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
  };
};

export default useProducts;

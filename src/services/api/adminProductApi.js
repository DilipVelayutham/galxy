import axios from 'axios';
import { API_BASE_URL } from '../../utils/constants';

/**
 * Axios instance configured for GALXY Admin API
 * Includes base URL, default headers, and interceptors
 */
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
});

// Request interceptor - attach auth token if available
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('admin_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - handle common errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      console.warn('Unauthorized - redirect to login');
    }
    return Promise.reject(error);
  }
);

/**
 * Admin Product API Service
 * Provides methods to interact with the admin product management REST API.
 *
 * NOTE: this file was previously named `productApi.js`, which is the exact
 * filename the public-facing module uses for its own (different) API
 * service. Keeping both modules' service files named identically would
 * cause one to silently overwrite the other the moment they land in the
 * same repo/services folder, so this file is named `adminProductApi.js`
 * to avoid that collision.
 */
const adminProductApi = {
  /**
   * Fetch all product categories (each carries attribute_schema, accent_color,
   * hero_image). Used to populate the category dropdown and to drive the
   * structured default_attributes inputs in ProductForm.
   * @returns {Promise} Axios response with categories data
   */
  getCategories: async () => {
    try {
      const response = await apiClient.get('/admin/categories');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch categories:', error);
      throw error;
    }
  },

  /**
   * Fetch all products with optional filters and pagination
   * @param {object} params - Query parameters { page, limit, search, category_id, stock_status, is_active }
   * @returns {Promise} Axios response with products data
   */
  getProducts: async (params = {}) => {
    try {
      const response = await apiClient.get('/admin/products', { params });
      return response.data;
    } catch (error) {
      console.error('Failed to fetch products:', error);
      throw error;
    }
  },

  /**
   * Fetch a single product by ID
   * @param {string} id - Product ID
   * @returns {Promise} Axios response with product data
   */
  getProductById: async (id) => {
    try {
      const response = await apiClient.get(`/admin/products/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Failed to fetch product ${id}:`, error);
      throw error;
    }
  },

  /**
   * Create a new product
   * @param {object} productData - Product data to create
   * @returns {Promise} Axios response with created product
   */
  createProduct: async (productData) => {
    try {
      const response = await apiClient.post('/admin/products', productData);
      return response.data;
    } catch (error) {
      console.error('Failed to create product:', error);
      throw error;
    }
  },

  /**
   * Update an existing product
   * @param {string} id - Product ID
   * @param {object} productData - Updated product data
   * @returns {Promise} Axios response with updated product
   */
  updateProduct: async (id, productData) => {
    try {
      const response = await apiClient.put(`/admin/products/${id}`, productData);
      return response.data;
    } catch (error) {
      console.error(`Failed to update product ${id}:`, error);
      throw error;
    }
  },

  /**
   * Delete a product
   * @param {string} id - Product ID
   * @returns {Promise} Axios response
   */
  deleteProduct: async (id) => {
    try {
      const response = await apiClient.delete(`/admin/products/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Failed to delete product ${id}:`, error);
      throw error;
    }
  },

  /**
   * Toggle product active status (deactivate/activate)
   * @param {string} id - Product ID
   * @param {boolean} isActive - New active status
   * @returns {Promise} Axios response
   */
  toggleProductStatus: async (id, isActive) => {
    try {
      const response = await apiClient.put(`/admin/products/${id}`, { is_active: isActive });
      return response.data;
    } catch (error) {
      console.error(`Failed to toggle product ${id} status:`, error);
      throw error;
    }
  },

  /**
   * Upload images for a product
   * @param {string} id - Product ID
   * @param {FormData} formData - FormData with image files
   * @param {Function} onUploadProgress - Progress callback
   * @returns {Promise} Axios response with uploaded image URLs
   */
  uploadImages: async (id, formData, onUploadProgress) => {
    try {
      const response = await apiClient.post(`/admin/products/${id}/images`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress,
      });
      return response.data;
    } catch (error) {
      console.error(`Failed to upload images for product ${id}:`, error);
      throw error;
    }
  },

  /**
   * Delete a product image
   * @param {string} productId - Product ID
   * @param {string} imageId - Image ID to delete
   * @returns {Promise} Axios response
   */
  deleteImage: async (productId, imageId) => {
    try {
      const response = await apiClient.delete(`/admin/products/${productId}/images/${imageId}`);
      return response.data;
    } catch (error) {
      console.error(`Failed to delete image ${imageId}:`, error);
      throw error;
    }
  },

  /**
   * Set thumbnail image for a product.
   * Uses the documented endpoint shape: PUT /admin/products/:id/thumbnail
   * with the image id in the request body (not embedded mid-path), matching
   * the spec exactly rather than the previous /images/:imageId/thumbnail path.
   * @param {string} productId - Product ID
   * @param {string} imageId - Image ID to set as thumbnail
   * @returns {Promise} Axios response
   */
  setThumbnail: async (productId, imageId) => {
    try {
      const response = await apiClient.put(`/admin/products/${productId}/thumbnail`, { imageId });
      return response.data;
    } catch (error) {
      console.error(`Failed to set thumbnail:`, error);
      throw error;
    }
  },
};

export default adminProductApi;
